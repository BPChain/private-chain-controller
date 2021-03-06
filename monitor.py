"""Monitor to report on all blockchain docker controllers"""
import copy
import json
import logging
import os
import socket
import time
import daemonize
import docker
import yaml
from websocket import create_connection

PID = "./status_monitor.pid"
CONFIG = {}
HOSTNAME = socket.gethostname()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARN)
LOGGER.propagate = False
FH = logging.FileHandler("./monitor.log", "w")
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
FH.setLevel(logging.WARN)
FH.setFormatter(FORMATTER)
LOGGER.addHandler(FH)
CONFIG_FILE = open(os.path.join(os.path.dirname(__file__), 'config.yaml'))
CONFIG_FILE_ID = CONFIG_FILE.fileno()

KEEP_FDS = [FH.stream.fileno(), CONFIG_FILE_ID]


# pylint: disable=broad-except
# pylint: disable=global-statement
# pylint: disable=too-many-nested-blocks


def start_socket():
    """Start the websocket and connect to the API Server."""
    reconnect = 0
    while reconnect < 20:
        try:
            LOGGER.debug('Create connection')
            web_socket = create_connection(CONFIG["url"])
            LOGGER.debug('Connection established')
            global HOSTNAME
            LOGGER.debug('Hostname: %s', HOSTNAME)
            reconnect = 0
            LOGGER.debug('Register with Server')
            LOGGER.debug('Registration completed')
            check_docker_state(web_socket)

        except Exception as exception:
            LOGGER.error('Connection error occured')
            LOGGER.error(exception)
            LOGGER.exception("message")

        reconnect += 1
        LOGGER.warn('Lost connection to server')
        time.sleep(5)
        LOGGER.warn('Try to reconnect')


def check_docker_state(web_socket):
    """Check the current state of all supported docker
    containers and report them to the websocket"""
    LOGGER.info('Start check_docker_state')
    client = docker.from_env()
    LOGGER.info(client.containers.list())
    current_docker_state = {}
    previous_docker_state = {}
    empty_docker_state = {
        "ethereum": {
            "miners": 0,
            "hosts": 0,
        },
        "xain": {
            "miners": 0,
            "hosts": 0,
        },
        "multichain": {
            "miners": 0,
            "hosts": 0,
        },
    }

    while True:
        current_docker_state = copy.deepcopy(empty_docker_state)
        LOGGER.debug("Checking docker containers:")
        for container in client.containers.list():
            LOGGER.debug(container.name)
            if CONFIG["chainContainerNames"]["ethereum"] in container.name:
                current_docker_state["ethereum"]["miners"] += 1
                current_docker_state["ethereum"]["hosts"] += 1
            if CONFIG["chainContainerNames"]["xain"] in container.name:
                current_docker_state["xain"]["miners"] += 1
                current_docker_state["xain"]["hosts"] += 1
            if CONFIG["chainContainerNames"]["multichain"] in container.name:
                current_docker_state["multichain"]["miners"] += 1
                current_docker_state["multichain"]["hosts"] += 1
        LOGGER.debug(str(current_docker_state))
        if current_docker_state == previous_docker_state:
            LOGGER.debug('Docker state stayed the same')
        else:
            LOGGER.debug('Docker state changed')
            LOGGER.debug('Send new state to Server')
            global HOSTNAME
            web_socket.send(json.dumps({
                "monitor": HOSTNAME,
                "state": current_docker_state,
            }))
        previous_docker_state = copy.deepcopy(current_docker_state)
        time.sleep(10)

    LOGGER.info('End check_docker_state')


def main():
    """Main method to init the monitor and start the websocket."""
    try:
        global CONFIG
        CONFIG = yaml.safe_load(CONFIG_FILE)
    except Exception as exception:
        LOGGER.error('Error occured while parsing config.yaml')
        LOGGER.error(exception)
    start_socket()


DAEMON = daemonize.Daemonize(
    app="blockchainMonitor", pid=PID, action=main, keep_fds=KEEP_FDS, chdir='./')
DAEMON.start()
