import json
from websocket import create_connection, WebSocket

activeChain = None

parameterList = [
  'numberOfHosts',
  'numberOfMiners',
  'switchChain',
]

chainList = [
  'ethereum',
  'xain',
  'multichain',
]

def checkCompleteness (object):
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


  if parameter != 'switchChain':
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

  return True

def startSocket() -> WebSocket:
  try:
    web_socket = create_connection("ws://172.16.64.115:4040")
    print("Connection established")
    waitingForInputs = True
    while waitingForInputs:
      message = web_socket.recv()
      print("Received '%s'" % message)
      if checkCompleteness(message):
        print('TODO')
  except Exception as exception:
        print("Error occured while waiting for transactions: ")
        print(exception)

if __name__ == "__main__":
  startSocket()
