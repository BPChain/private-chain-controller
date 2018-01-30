const io = require('socket.io-client')

const config = require('./config')
let activeChain = null

module.exports = async (options = {}) => {
  const {
    url,
    port,
    log,
  } = options
  const socket = io.connect(`${url}:${port}`)

  socket.on('connect', () => {
    log.info('Successfully connected!')
  })

  socket.on('messages', data => {
    if (JSON.parse(data)) {
      const instruction = JSON.parse(data)
      if (!instruction.action) {
        log.warn('Server did not specify the action')
        return
      }


      if (instruction.action === 'scale' &&
        instruction.content >= 0) {
        log.info(`Scale docker to ${instruction.content}`)
      }
      else if (
        instruction.action === 'change' &&
      instruction.content !== activeChain &&
      config.chains.includes(instruction.content)
      ) {
        activeChain = instruction.content
        log.info(`Change Blockchain to ${instruction.content}`)
      }
      else {
        log.warn(`Server sent wrong parameters: ${data}`)
      }
    }
    else {
      log.warn('Server did not sent a JSON object')
    }
  })
}
