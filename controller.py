"""Controller to handle all blockchains in the backend and connect to the aggregation server"""
import json
import logging
import os
import subprocess
import socket
import atexit
import time
import daemonize
import yaml
from websocket import create_connection

PID = "./controller.pid"

CONFIG = {}
ACTIVE_CHAIN_NAMES = []

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.propagate = False
FH = logging.FileHandler("./logfile.log", "w")
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s at: '%(lineno)d'")
FH.setLevel(logging.DEBUG)
FH.setFormatter(FORMATTER)
LOGGER.addHandler(FH)

CONFIG_FILE = open(os.path.join(os.path.dirname(__file__), 'config.yaml'))
CONFIG_FILE_ID = CONFIG_FILE.fileno()

KEEP_FDS = [FH.stream.fileno(), CONFIG_FILE_ID]


# pylint: disable=broad-except
# pylint: disable=global-statement
# pylint: disable=too-many-nested-blocks

def start_chain(chain_name):
    """Start a given chain."""
    global ACTIVE_CHAIN_NAMES
    path = CONFIG['chainScripts']['start'].format(str(chain_name))
    LOGGER.info("path %s", path)
    result = subprocess.run([str(path)], stdout=subprocess.PIPE)
    LOGGER.info("return code %d", result.returncode)
    LOGGER.info(result)
    ACTIVE_CHAIN_NAMES.append(chain_name)


def stop_chain(chain_name):
    """Stop a given chain."""
    path = CONFIG['chainScripts']['stop'].format(str(chain_name))
    LOGGER.info('stopping: %a', path)
    subprocess.Popen([str(path)], stdout=open(os.devnull, 'wb'))


def scale_hosts(chain_name, value):
    """Scale the number of Hosts"""
    global ACTIVE_CHAIN_NAMES
    if chain_name in ACTIVE_CHAIN_NAMES:
        path = CONFIG['chainScripts']['scaleLazy'].format(str(chain_name))
        subprocess.Popen([str(path), str(value)],
                         stdout=open(os.devnull, 'wb'))


def scale_miners(chain_name, value):
    """Scale the number of Miners."""
    global ACTIVE_CHAIN_NAMES
    if chain_name in ACTIVE_CHAIN_NAMES:
        path = CONFIG['chainScripts']['scaleMiner'].format(str(chain_name))
        subprocess.Popen([str(path), str(value)],
                         stdout=open(os.devnull, 'wb'))


def set_scenario_parameters(chain_name, scenario):
    """Set scenario period and payloadSize."""
    LOGGER.info(scenario)
    data = json.dumps(scenario['logContent'])
    LOGGER.info(data)
    if chain_name in ACTIVE_CHAIN_NAMES:
        LOGGER.debug('Setting for %s is %s ', chain_name, data)
        port = CONFIG['{}Port'.format(chain_name)]
        docker_websocket = create_connection("ws://localhost:{}".format(port))
        docker_websocket.send(data)
        docker_websocket.close()


def dispatch_action(chain_name, parameter, value, scenario):
    """Dispatch the parameters and values to the chain."""
    if parameter == 'numberofhosts':
        LOGGER.debug('Scale %s hosts to %d', chain_name, value)
        scale_hosts(chain_name, value)

    if parameter == 'numberofminers':
        LOGGER.debug('Scale %s miners to %d', chain_name, value)
        scale_miners(chain_name, value)

    if parameter == 'startchain':
        LOGGER.debug('Start %s', chain_name)
        start_chain(chain_name)

    if parameter == 'stopchain':
        LOGGER.debug('Stop %s', chain_name)
        stop_chain(chain_name)
        ACTIVE_CHAIN_NAMES.remove(chain_name)
        LOGGER.info("ACTIVE CHAIN NAMES %s", ACTIVE_CHAIN_NAMES)

    if scenario:
        LOGGER.debug('Sending scenario parameters to %s', chain_name)
        set_scenario_parameters(chain_name, scenario)


def enact_job(job):
    """Enact the retrieved job on the given chain."""
    for chain in CONFIG['chains']:
        if chain['chainName'].lower() == job['chainName'].lower():
            chain_name = chain['chainName']
            for parameter in job['parameters']:
                LOGGER.debug(parameter)
                for available_parameter in chain['parameter']:
                    if parameter.lower() == available_parameter['selector'].lower():
                        selected_parameter = available_parameter['selector'].lower()
                        try:
                            scenario = job['scenario']
                            LOGGER.info(scenario)
                            dispatch_action(
                                chain_name,
                                selected_parameter,
                                job['parameters'][available_parameter['selector']],
                                scenario)
                        except Exception as exception:
                            LOGGER.error('Error occured when dispatching job')
                            LOGGER.error(exception)


def init_controller():
    """Load and parse the config file."""
    try:
        global CONFIG
        CONFIG = yaml.safe_load(CONFIG_FILE)
    except Exception as exception:
        LOGGER.debug('Error occured while parsing config.yaml')
        LOGGER.debug(exception)


def start_socket():
    """Start the websocket and connect to the API Server."""
    reconnect = 0
    while reconnect < 20:
        try:
            reconnect, api_server_connection = connect_to_api_server()
            waiting_for_inputs = True
            while waiting_for_inputs:
                message = api_server_connection.recv()
                LOGGER.debug('Received %s', message)
                try:
                    job = json.loads(message)
                    enact_job(job)
                except Exception as exception:
                    LOGGER.debug('Error occured. Can not parse JSON %s', exception)

        except Exception as exception:
            LOGGER.debug('Connection error occured %s', exception)

        reconnect += 1
        LOGGER.debug('Lost connection to server')
        time.sleep(5)
        LOGGER.debug('Try to reconnect')


def stop_all_chains():
    global ACTIVE_CHAIN_NAMES
    for chain in ACTIVE_CHAIN_NAMES:
        stop_chain(chain)
    ACTIVE_CHAIN_NAMES = []


def connect_to_api_server():
    stop_all_chains()
    hostname = socket.gethostname()
    web_socket = create_connection(CONFIG['url'])
    LOGGER.debug('Created connection')
    LOGGER.debug('Hostname: %s', hostname)
    LOGGER.debug('Send chain configuration options')
    data = {
        'target': hostname,
        'chains': CONFIG['chains'],
    }
    web_socket.send(json.dumps(data))
    LOGGER.debug('Chain configuration options sent')
    return 0, web_socket


def exit_controller():
    """Exit from the controller and stop all active chains."""
    LOGGER.debug('Stopping active chains %s', ACTIVE_CHAIN_NAMES)
    stop_all_chains()


def main():
    """Main method to init the controller and start the websocket."""
    init_controller()
    start_socket()


atexit.register(exit_controller)

DAEMON = daemonize.Daemonize(
    app="blockchainController", pid=PID, action=main, keep_fds=KEEP_FDS, chdir='./')
DAEMON.start()
