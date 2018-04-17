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
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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
    global ACTIVE_CHAIN_NAMES
    path = CONFIG['chainScripts']['stop'].format(str(chain_name))
    subprocess.Popen([str(path)], stdout=open(os.devnull, 'wb'))
    ACTIVE_CHAIN_NAMES.remove(chain_name)


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


def set_scenario_parameters(chain_name, period, payload_size):
    """Set scenario period and payloadSize."""
    global ACTIVE_CHAIN_NAMES
    if chain_name in ACTIVE_CHAIN_NAMES:
        LOGGER.debug('Setting ' + chain_name + ' period to: ' + str(period))
        LOGGER.debug('Setting ' + chain_name +
                     ' payloadSize to: ' + str(payload_size))
        port = CONFIG['{}Port'.format(chain_name)]
        docker_websocket = create_connection("ws://localhost:{}".format(port))
        data = json.dumps({"period": period, "payloadSize": payload_size})
        docker_websocket.send(data)
        docker_websocket.close()


def dispatch_action(chain_name, parameter, value):
    """Dispatch the parameters and values to the chain."""
    global ACTIVE_CHAIN_NAMES
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

    if parameter == 'scenario':
        LOGGER.debug('Sending scenario parameters to %s', chain_name)
        set_scenario_parameters(chain_name, value['period'], value['payloadSize'])


def enact_job(job):
    """Enact the retrieved job on the given chain."""
    global ACTIVE_CHAIN_NAMES
    for chain in CONFIG['chains']:
        if chain['chainName'].lower() == job['chainName'].lower():
            chain_name = chain['chainName']
            for parameter in job['parameters']:
                LOGGER.debug(parameter)
                for available_parameter in chain['parameter']:
                    if parameter.lower() == available_parameter['selector'].lower():
                        selected_parameter = available_parameter['selector'].lower(
                        )
                        try:
                            dispatch_action(
                                chain_name,
                                selected_parameter,
                                job['parameters'][available_parameter['selector']])
                        except Exception as exception:
                            LOGGER.debug('Error occured when dispatching job')
                            LOGGER.debug(exception)


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
    global ACTIVE_CHAIN_NAMES
    reconnect = 0
    while reconnect < 20:
        try:
            if ACTIVE_CHAIN_NAMES:
                for chain in ACTIVE_CHAIN_NAMES:
                    stop_chain(chain)

            LOGGER.debug('Create connection')
            hostname = socket.gethostname()
            web_socket = create_connection(CONFIG['url'])
            LOGGER.debug('Connection established')
            LOGGER.debug('Hostname: %s', hostname)
            reconnect = 0
            LOGGER.debug('Send chain configuration options')
            data = {
                'target': hostname,
                'chains': CONFIG['chains'],
            }
            web_socket.send(json.dumps(data))
            LOGGER.debug('Chain configuration options sent')

            waiting_for_inputs = True
            while waiting_for_inputs:
                message = web_socket.recv()
                LOGGER.debug('Received %s', message)
                try:
                    job = json.loads(message)
                    enact_job(job)
                except Exception as exception:
                    LOGGER.debug('Error occured. Can not parse JSON')
                    LOGGER.debug(exception)

        except Exception as exception:
            LOGGER.debug('Connection error occured')
            LOGGER.debug(exception)

        reconnect += 1
        LOGGER.debug('Lost connection to server')
        time.sleep(5)
        LOGGER.debug('Try to reconnect')


def exit_controller():
    """Exit from the controller and stop all active chains."""
    global ACTIVE_CHAIN_NAMES
    LOGGER.debug('Stopping active chains')
    for chain in ACTIVE_CHAIN_NAMES:
        stop_chain(chain)


def main():
    """Main method to init the controller and start the websocket."""
    init_controller()
    start_socket()


atexit.register(exit_controller)

DAEMON = daemonize.Daemonize(
    app="blockchainController", pid=PID, action=main, keep_fds=KEEP_FDS, chdir='./')
DAEMON.start()
