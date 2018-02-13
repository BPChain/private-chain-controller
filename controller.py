import json
from websocket import create_connection, WebSocket
import subprocess
import socket


if __name__ == "__main__":
  activeChain = None
  hostname = socket.gethostname()
  parameterList = [
      'numberOfHosts',
      'numberOfMiners',
      'switchChain',
      'startChain',
  ]
  chainList = [
      'ethereum',
      'xain',
      'multichain',
  ]
  startSocket()


def checkCompleteness(object):
    dictionary = json.loads(object)
    chain = dictionary["chain"]
    parameter = dictionary["parameter"]
    value = dictionary["value"]

    if not chain and activeChain:
        print('Server did not specify a chain')
        return False

    if not parameter:
        print('Server did not specify a parameter')
        return False

    if not value:
        print('Server did not specify a value')
        return False

    if not chain in chainList and activeChain:
        print('Chain ${chain} does not exist')
        return False

    if chain != activeChain and activeChain:
        print('Server tried to change an other chain')
        return False

    if not parameter in parameterList:
        print('Parameter ${parameter} is unknown')
        return False

    if parameter != 'switchChain' and parameter != 'startChain':
        try:
            if int(value) < 0 or int(value) > 50:
                print('Can not set parameter to value')
                return False
        except Exception as exception:
            print('Value is string')
            return False

    if parameter is 'switchChain' and (activeChain == value or value not in chainList):
        print('Can not switch chain ${activeChain} to ${value}')
        return False

    if parameter is 'startChain' and (activeChain != None or value not in chainList):
        print('Can not start chain ${value}, ${activeChain} is already running!')
        return False

    return True


def startSocket():
    try:
	      print("Create Connection")
        web_socket = create_connection("wss://bpt-lab.org/bp2017w1-controller")
        print(hostname)
        print(activeChain)
        web_socket.send('{name: ${hostname}, chain: ${activeChain}}')
        print("Connection established")
        waitingForInputs = True
        while waitingForInputs:
            message = web_socket.recv()
            print("Received '%s'" % message)
            if checkCompleteness(message):
                messageBody = json.loads(message)
                chain = messageBody["chain"]
                parameter = messageBody["parameter"]
                value = messageBody["value"]
                if parameter == 'switchChain':
                    output = subprocess.check_output(
                        ['./private_chain_scripts/switchChainToFrom.sh', str(chain), str(activeChain)])
                    print(output)
                if parameter == 'numberOfHost':
                    path = "./private_chain_scripts/lazyNodes_{}.sh".format(
                        chain)
                    output = subprocess.check_output([path, str(value)])
                    print(output)
                if parameter == 'numberOfMiners':
                    path = "./private_chain_scripts/scale_{}.sh".format(
                        chain)
                    output = subprocess.check_output([path, str(value)])
                    print(output)
                if parameter == 'startChain':
                    activeChain = value
		    path = "./private_chain_scripts/start_{}.sh".format(activeChain)
                    subprocess.Popen(
                        ["bash", path])
    except Exception as exception:
        print("Error occured while waiting for transactions: ")
        print(exception)
