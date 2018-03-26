import json
import yaml
from websocket import create_connection, WebSocket
import subprocess
import socket
import os


config = {}

def dispatchJob(job):
  for chain in (config['chains']):
    if chain['chainName'] is job['chainName']:
      print(chain['chainName'])
      for parameter in chain['parameter']:
        print(parameter['name'])

def initController():
  try:
    global config
    config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml')))
  except Exception as exception:
    print("Error occured while parsing config.yaml")
    print(exception)

def startSocket():
  try:
    activeChainName = None
    print("Create connection")
    hostname = socket.gethostname()
    web_socket = create_connection(config['url'])
    print("Connection established")
    print("Hostname: " + hostname)
    print("Send chain configuration options")
    data = {
      'target': config['target'],
      'chains': config['chains'],
    }
    web_socket.send(json.dumps(data))
    print("Chain configuration options sent")


    waitingForInputs = True
    while waitingForInputs:
      message = web_socket.recv()
      print("Received '%s'" % message)
      try:
        job = json.loads(message)
        dispatchJob(job)
      except Exception as exception:
        print("Error occured. Can not parse JSON")
        print(exception)


  except Exception as exception:
    print("Connection error occured")
    print(exception)
    return False


if __name__ == "__main__":
  initController()
  startSocket()

"""
messageBody = json.loads(message)
        chain = messageBody["chain"]
        parameter = messageBody["parameter"]
        value = messageBody["value"]
        if parameter == 'switchChain':
            subprocess.Popen(['./private_chain_scripts/switchChainToFrom.sh', str(chain), str(activeChainName)])
        if parameter == 'numberOfHost':
            path = "./private_chain_scripts/lazyNodes_{}.sh".format(
                chain)
            subprocess.Popen([str(path), str(value)])
        if parameter == 'numberOfMiners':
            path = "./private_chain_scripts/scale_{}.sh".format(
                chain)
            subprocess.Popen([str(path), str(value)])
        if parameter == 'startChain':
            activeChain = value
            activeChainName = value
            path = "./private_chain_scripts/start_{}.sh".format(
                activeChainName)
            subprocess.Popen(["bash", path])
"""
