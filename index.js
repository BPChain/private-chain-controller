const startClient = require('./startClient')
const config = require('./config')

const log = console

log.info('Start client')
startClient({
  url: config.url,
  port: config.port,
  log,
})
