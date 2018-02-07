from __future__ import absolute_import
import json
from websocket import create_connection, WebSocket

activeChain = None

parameterList = [
    u'numberOfHosts',
    u'numberOfMiners',
    u'switchChain',
    u'startChain',
]

chainList = [
    u'ethereum',
    u'xain',
    u'multichain',
]


def checkCompleteness(object):
    dictionary = json.loads(object)
    chain = dictionary[u"chain"]
    parameter = dictionary[u"parameter"]
    value = dictionary[u"value"]

    if not chain and activeChain:
        print u'Server did not specify a chain'
        return False

    if not parameter:
        print u'Server did not specify a parameter'
        return False

    if not value:
        print u'Server did not specify a value'
        return False

    if not chain in chainList and activeChain:
        print u'Chain ${chain} does not exist'
        return False

    if chain != activeChain and activeChain:
        print u'Server tried to change an other chain'
        return False

    if not parameter in parameterList:
        print u'Parameter ${parameter} is unknown'
        return False

    if parameter != u'switchChain' and parameter != u'startChain':
        try:
            if int(value) < 0 or int(value) > 50:
                print u'Can not set parameter to value'
                return False
        except Exception, exception:
            print u'Value is string'
            return False

    if parameter is u'switchChain' and (activeChain == value or value not in chainList):
        print u'Can not switch chain ${activeChain} to ${value}'
        return False

    if parameter is u'startChain' and (activeChain != None or value not in chainList):
        print u'Can not start chain ${value}, ${activeChain} is already running!'
        return False

    return True


def startSocket():
    try:
        web_socket = create_connection(u"ws://172.16.64.115:4040")
        print u"Connection established"
        waitingForInputs = True
        while waitingForInputs:
            message = web_socket.recv()
            print u"Received '%s'" % message
            if checkCompleteness(message):
                messageBody = json.loads(message)
                chain = messageBody[u"chain"]
                parameter = messageBody[u"parameter"]
                value = messageBody[u"value"]
                if parameter == u'switchChain':
                    output = subprocess.check_output(
                        [u'./private_chain_scripts/switchChainToFrom.sh', unicode(chain), unicode(activeChain)])
                    print output
                if parameter == u'numberOfHost':
                    path = u"./private_chain_scripts/lazyNodes_{}.sh".format(
                        chain)
                    output = subprocess.check_output([path, unicode(value)])
                    print output
                if parameter == u'numberOfMiners':
                    path = u"./private_chain_scripts/scale_{}.sh".format(
                        chain)
                    output = subprocess.check_output([path, unicode(value)])
                    print output
                if parameter == u'startChain':
                    activeChain = chain
                    subprocess.Popen(
                        [u"bash", u"./private_chain_scripts/startChain.sh", unicode(chain)])
    except Exception, exception:
        print u"Error occured while waiting for transactions: "
        print exception


if __name__ == u"__main__":
    startSocket()
