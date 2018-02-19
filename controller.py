import json
from websocket import create_connection, WebSocket
import subprocess
import socket

def checkCompleteness(object):
    dictionary = json.loads(object)
    chain = dictionary["chain"]
    parameter = dictionary["parameter"]
    value = dictionary["value"]

    if not chain and activeChain is not None:
        print('Server did not specify a chain')
        return False

    if not parameter:
        print('Server did not specify a parameter')
        return False

    if not value:
        print('Server did not specify a value')
        return False

    if chain not in chainList and activeChain is not None:
        print('Chain ${chain} does not exist')
        return False

    if chain != activeChain and activeChain is not None:
        print('Server tried to change an other chain')
        return False

    if parameter not in parameterList:
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

    if parameter is 'startChain' and (activeChain is not None or value not in chainList):
        print(
            'Can not start chain ${value}, ${activeChain} is already running!')
        return False

    return True


def startSocket():
    try:
        global activeChain
        global hostname
        if activeChain is None:
            activeChainName = "None"
        else:
            activeChainName = activeChain
        print("Create Connection")
        web_socket = create_connection("wss://bpt-lab.org/bp2017w1-controller")
        print(hostname)
        data = {'name': hostname, 'chain': activeChainName}
        web_socket.send(json.dumps(data))
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
    except Exception as exception:
        print("Error occured while waiting for transactions: ")
        print(exception)


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
