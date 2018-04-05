import json
from modules import yaml
from modules.websocket import create_connection, WebSocket
import subprocess
import socket
import os
import time


config = {}
activeChainName = None

def startChain(chainName):
  path = config['chainScripts']['start'].format(str(chainName))
  subprocess.Popen([str(path)])
  activeChainName = chainName

def stopChain(chainName):
  path = config['chainScripts']['stop']
  subprocess.Popen([str(path), str(chainName)])
  activeChainName = None

def switchChainTo(chainName):
  path = config['chainScripts']['switch']
  subprocess.Popen([str(path), str(chainName), str(activeChainName)])
  activeChainName = chainName

def scaleHosts(chainName, value):
  path = config['chainScripts']['scaleLazy'].format(str(chainName))
  subprocess.Popen([str(path), str(value)])

def scaleMiners(chainName, value):
  path = config['chainScripts']['scaleMiner'].format(str(chainName))
  subprocess.Popen([str(path), str(value)])

def dispatchAction(chainName, parameter, value):
  if parameter == 'numberofhosts':
    print('Scale ' + chainName + ' hosts to ' + value)
    scaleHosts(chainName, value)

  if parameter == 'numberofminers':
    print('Scale ' + chainName + ' miners to ' + value)
    scaleMiners(chainName, value)

  if parameter == 'startchain':
    print('Start ' + chainName)
    startChain(chainName)

  if parameter == 'stopchain':
    print('Stop ' + chainName)
    stopChain(chainName)

  if parameter == 'switchchain':
    print('Switch ' + activeChainName + ' to ' + chainName)
    switchChainTo(chainName)

def enactJob(job):
  for chain in (config['chains']):
    if chain['chainName'].lower() == job['chainName'].lower():
      chainName = chain['chainName']
      for parameter in job['parameters']:
        print(parameter)
        for availableParameter in chain['parameter']:
          if parameter.lower() == availableParameter['selector'].lower():
            selectedParameter = availableParameter['selector'].lower()
            try:
              dispatchAction(chainName, selectedParameter, job['parameters'][availableParameter['selector']])
            except Exception as exception:
              print('Error occured when dispatching job')
              print(exception)



def initController():
  try:
    global config
    config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml')))
  except Exception as exception:
    print('Error occured while parsing config.yaml')
    print(exception)

def startSocket():
  reconnect = 0
  while(reconnect < 20):
    try:
      if activeChainName != None:
        stopChain(activeChainName)

      print('Create connection')
      hostname = socket.gethostname()
      web_socket = create_connection(config['url'])
      print('Connection established')
      print('Hostname: ' + hostname)
      reconnect = 0
      print('Send chain configuration options')
      data = {
        'target': hostname,
        'chains': config['chains'],
      }
      web_socket.send(json.dumps(data))
      print('Chain configuration options sent')


      waitingForInputs = True
      while waitingForInputs:
        message = web_socket.recv()
        print('Received ' + message)
        try:
          job = json.loads(message)
          enactJob(job)
        except Exception as exception:
          print('Error occured. Can not parse JSON')
          print(exception)


    except Exception as exception:
      print('Connection error occured')
      print(exception)

    reconnect += 1
    print('Lost connection to server')
    time.sleep(5)
    print('Try to reconnect')


if __name__ == '__main__':
  initController()
  startSocket()
