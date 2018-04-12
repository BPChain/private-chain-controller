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
activeChainNames = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("./logfile.log", "w")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

configFile = open(os.path.join(os.path.dirname(__file__), 'config.yaml'))
configFileId = configFile.fileno()

keep_fds = [fh.stream.fileno(), configFileId]

def startChain(chainName):
  global activeChainNames
  path = config['chainScripts']['start'].format(str(chainName))
  subprocess.Popen([str(path)], stdout=open(os.devnull, 'wb'))
  activeChainNames.append(chainName)

def stopChain(chainName):
  global activeChainNames
  path = config['chainScripts']['stop'].format(str(chainName))
  subprocess.Popen([str(path)], stdout=open(os.devnull, 'wb'))
  activeChainNames.remove(chainName)

def scaleHosts(chainName, value):
  global activeChainNames
  if chainName in activeChainNames:
    path = config['chainScripts']['scaleLazy'].format(str(chainName))
    subprocess.Popen([str(path), str(value)], stdout=open(os.devnull, 'wb'))

def scaleMiners(chainName, value):
  global activeChainNames
  if chainName in activeChainNames:
    path = config['chainScripts']['scaleMiner'].format(str(chainName))
    subprocess.Popen([str(path), str(value)], stdout=open(os.devnull, 'wb'))

def setScenarioParameters(chainName, frequency, payloadSize):
  global activeChainNames
  if chainName in activeChainNames:
    logger.debug('Setting'+ chainName + 'frequency to: ' + frequency)
    logger.debug('Setting'+ chainName + 'payloadSize to: ' + payloadSize)
    port = config['{}Port'.format(chainName)]
    ws = create_connection("ws://localhost:{}".format(port))
    data = json.dumps({"frequency": frequency, "payloadSize": payloadSize})
    ws.send(data)
    ws.close()

def dispatchAction(chainName, parameter, value):
  global activeChainNames
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

  if parameter == 'scenario':
    logger.debug('Sending scenario parameters to ' + chainName)
    setScenarioParameters(chainName, value['frequency'], value['payloadSize'])

def enactJob(job):
  global activeChainNames
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
  global activeChainNames
  reconnect = 0
  while(reconnect < 20):
    try:
      if activeChainNames:
        for chain in activeChainNames:
          stopChain(chain)

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
  global activeChainNames
  logger.debug('Stopping active chains')
  if not activeChainNames:
    for chain in activeChainNames:
      stopChain(chain)

def main():
  initController()
  startSocket()

exitFunct.register_exit_fun(exit)

daemon = daemonize.Daemonize(app="blockchainController", pid=pid, action=main, keep_fds=keep_fds, chdir='./')
daemon.start()
