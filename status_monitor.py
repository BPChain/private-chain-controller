"""Monitor to report on all blockchain docker controllers"""
import json
import logging
import os
import subprocess
import socket
import atexit
import time
import daemonize
import docker
import yaml
from websocket import create_connection

PID = "./status_monitor.pid"

CONFIG = {}
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.propagate = False
FH = logging.FileHandler("./monitor.log", "w")
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


def start_socket():
    """Start the websocket and connect to the API Server."""
    global ACTIVE_CHAIN_NAMES
    reconnect = 0
    while reconnect < 20:
        try:
            LOGGER.debug('Create connection')
            hostname = socket.gethostname()
            web_socket = create_connection(CONFIG['url'])
            LOGGER.debug('Connection established')
            LOGGER.debug('Hostname: %s', hostname)
            reconnect = 0
            LOGGER.debug('Register with Server')
            data = {
                'monitor': hostname,
            }
            web_socket.send(json.dumps(data))
            LOGGER.debug('Registration completed')

            check_docker_state(web_socket)

        except Exception as exception:
            LOGGER.error('Connection error occured')
            LOGGER.error(exception)

        reconnect += 1
        LOGGER.warning('Lost connection to server')
        time.sleep(5)
        LOGGER.warning('Try to reconnect')


def check_docker_state(websocket):
    LOGGER.info('Start check_docker_state')
    client = docker.from_env()
    LOGGER.info(client.containers.list())
    docker_state = {
        'ethereum': {
            'miners': 0,
            'hosts': 0,
        },
        'xain': {
            'miners': 0,
            'hosts': 0,
        },
        'multichain': {
            'miners': 0,
            'hosts': 0,
        },
    }

    LOGGER.info(docker_state)

    while True:
        previous_docker_state = docker_state
        for container in client.containers.list():
            if CONFIG['ethereum'] in container.name:
                docker_state['ethereum']['miners'] += 1
                docker_state['ethereum']['hosts'] += 1
            if CONFIG['ethereumLazy'] in container.name:
                docker_state['ethereum']['hosts'] += 1
            if CONFIG['xain'] in container.name:
                docker_state['xain']['miners'] += 1
                docker_state['xain']['hosts'] += 1
            if CONFIG['xainLazy'] in container.name:
                docker_state['xain']['hosts'] += 1
            if CONFIG['multichain'] in container.name:
                docker_state['multichain']['miners'] += 1
                docker_state['multichain']['hosts'] += 1
        LOGGER.debug(docker_state)
        if previous_docker_state == docker_state:
          LOGGER.debug('Docker state stayed the same')
        else:
          LOGGER.debug('Docker state changed')
          LOGGER.debug('Send new state to Server')

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
