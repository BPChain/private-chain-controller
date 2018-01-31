const WebSocket = require('ws')

const config = require('./config')

module.exports = async (options = {}) => {
  const {
    url,
    log,
  } = options
  let {activeChain} = options

  function isNumeric (number) {
    return !isNaN(parseInt(number)) && isFinite(number)
  }

  function checkCompleteness (object = {}) {
    const {
      chain,
      parameter,
      value,
    } = object

    if (!chain && activeChain) {
      log.warn('Server did not specify a chain')
      return false
    }
    if (!parameter) {
      log.warn('Server did not specify a parameter')
      return false
    }
    if (!value) {
      log.warn('Server did not specify a value')
      return false
    }
    if (!config.chains.includes(chain) && activeChain) {
      log.warn(
        `Chain ${chain} does not exist`
      )
      return false
    }
    if (chain !== activeChain && activeChain) {
      log.warn(
        `Server tried to change an other chain (${chain} != ${activeChain})`
      )
      return false
    }
    if (!config.parameters.includes(parameter)) {
      log.warn(`Parameter ${parameter} is unknown`)
      return false
    }
    if (
      parameter !== 'switchChain' &&
      (!isNumeric(value) || value < 0 || value > 50)
    ) {
      log.warn(`Can not set ${parameter} to ${value}`)
      return false
    }
    if (
      parameter === 'switchChain' &&
      (activeChain === value ||
      typeof value !== 'string' || !config.chains.includes(value))
    ) {
      log.info(`Can not switch chain ${activeChain} to ${value}`)
      return false
    }
    return true
  }


  function executeRequest (object = {}) {
    const {
      chain,
      parameter,
      value,
    } = object
    if (parameter === 'switchChain') {
      activeChain = value
    }
    log.info(`Apply on ${chain} ${parameter} = ${value}`)
  }

  const ws = new WebSocket(url)

  ws.on('open', () => {
    ws.send('open connection')
  })

  ws.on('messages', data => {
    try {
      const instruction = JSON.parse(data)
      if (checkCompleteness(instruction)) {
        executeRequest(instruction)
      }
    }
    catch (error) {
      log.error(`Server did not sent a JSON object: ${error.message}`)
    }
  })
}
