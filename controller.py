from modules.daemonize import daemonize
from modules.exitFunct import exitFunct
import json
import logging
from modules import yaml
from modules.websocket import create_connection, WebSocket
import subprocess
import socket
import os
import time

pid = "./controller.pid"

config = {}
activeChainName = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("./logfile.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

configFile = open(os.path.join(os.path.dirname(__file__), 'config.yaml'))
configFileId = configFile.fileno()

keep_fds = [fh.stream.fileno(), configFileId]

def startChain(chainName):
  path = config['chainScripts']['start'].format(str(chainName))
  subprocess.Popen([str(path)], stdout=open(os.devnull, 'wb'))
  activeChainName = chainName

def stopChain(chainName):
  path = config['chainScripts']['stop']
  subprocess.Popen([str(path), str(chainName)], stdout=open(os.devnull, 'wb'))
  activeChainName = None

def switchChainTo(chainName):
  path = config['chainScripts']['switch']
  subprocess.Popen([str(path), str(chainName), str(activeChainName)], stdout=open(os.devnull, 'wb'))
  activeChainName = chainName

def scaleHosts(chainName, value):
  path = config['chainScripts']['scaleLazy'].format(str(chainName))
  subprocess.Popen([str(path), str(value)], stdout=open(os.devnull, 'wb'))

def scaleMiners(chainName, value):
  path = config['chainScripts']['scaleMiner'].format(str(chainName))
  subprocess.Popen([str(path), str(value)], stdout=open(os.devnull, 'wb'))

def dispatchAction(chainName, parameter, value):
  if parameter == 'numberofhosts':
    logger.debug('Scale ' + chainName + ' hosts to ' + value)
    scaleHosts(chainName, value)

  if parameter == 'numberofminers':
    logger.debug('Scale ' + chainName + ' miners to ' + value)
    scaleMiners(chainName, value)

  if parameter == 'startchain':
    logger.debug('Start ' + chainName)
    startChain(chainName)

  if parameter == 'stopchain':
    logger.debug('Stop ' + chainName)
    stopChain(chainName)

  if parameter == 'switchchain':
    logger.debug('Switch ' + activeChainName + ' to ' + chainName)
    switchChainTo(chainName)

def enactJob(job):
  for chain in (config['chains']):
    if chain['chainName'].lower() == job['chainName'].lower():
      chainName = chain['chainName']
      for parameter in job['parameters']:
        logger.debug(parameter)
        for availableParameter in chain['parameter']:
          if parameter.lower() == availableParameter['selector'].lower():
            selectedParameter = availableParameter['selector'].lower()
            try:
              dispatchAction(chainName, selectedParameter, job['parameters'][availableParameter['selector']])
            except Exception as exception:
              logger.debug('Error occured when dispatching job')
              logger.debug(exception)



def initController():
  try:
    global config
    config = yaml.safe_load(configFile)
  except Exception as exception:
    logger.debug('Error occured while parsing config.yaml')
    logger.debug(exception)

def startSocket():
  reconnect = 0
  while(reconnect < 20):
    try:
      if activeChainName != None:
        stopChain(activeChainName)

      logger.debug('Create connection')
      hostname = socket.gethostname()
      web_socket = create_connection(config['url'])
      logger.debug('Connection established')
      logger.debug('Hostname: ' + hostname)
      reconnect = 0
      logger.debug('Send chain configuration options')
      data = {
        'target': hostname,
        'chains': config['chains'],
      }
      web_socket.send(json.dumps(data))
      logger.debug('Chain configuration options sent')


      waitingForInputs = True
      while waitingForInputs:
        message = web_socket.recv()
        logger.debug('Received ' + message)
        try:
          job = json.loads(message)
          enactJob(job)
        except Exception as exception:
          logger.debug('Error occured. Can not parse JSON')
          logger.debug(exception)


    except Exception as exception:
      logger.debug('Connection error occured')
      logger.debug(exception)

    reconnect += 1
    logger.debug('Lost connection to server')
    time.sleep(5)
    logger.debug('Try to reconnect')

def exit():
  if activeChainName != None:
    stopChain(activeChainName)

def main():
  initController()
  startSocket()

exitFunct.register_exit_fun(cleanup)

daemon = daemonize.Daemonize(app="blockchainController", pid=pid, action=main, keep_fds=keep_fds)
daemon.start()
