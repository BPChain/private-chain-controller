const io = require('socket.io-client')
const socket = io.connect('http://localhost:4000')

const config = require('./config')

let activeChain = null

socket.on('connect', server => {
  console.log('Successfully connected!')
})

socket.on('messages', data => {
  if (data.action === 'scale' && data.content > 0) {
    console.info(`Scale docker to ${data.content}`)
  }
  else if (
    data.action === 'change'
    && data.content != activeChain
    && config.chains.includes(data.content)
  ) {
    console.info(`Change Blockchain to ${data.content}`)
  }
})
