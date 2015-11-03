var http = require('http').Server(null)
var io = require('socket.io')(http)
var config = require('./config/config.json')

var MongoClient = require('mongodb').MongoClient
var assert = require('assert')

var CronJob = require('cron').CronJob

var clients = {}
var checked = []

var DEBUG = function (message) {
  if (config.debug && config.debug == true) {
    console.log(message)
  }
}

var dataHandlerCb = function (data) {
  MongoClient.connect(config.url, function (err, db) {
    assert.equal(null, err)
    collection = db.collection(config.collection)
    collection.insert(data, function (err, result) {
      assert.equal(err, null)
      db.close()
    })
  })
}

var requestData = function (client) {
  if (Object.keys(clients).length == 0) return; // don't bother if there are no clients

  // Check the current client and checked list, clearing if needed
  if (checked.length >= Object.keys(clients).length) {
    checked = []
  }

  var c
  if (client) {
    // Request data from specific client
    c = client
  } else {
    // Get a random client
    var k = Object.keys(clients)[Math.floor(Math.random() * Object.keys(clients).length)]
    c = clients[k].socket
  }

  if (checked.indexOf(c.id) == -1) {
    // Tell the client to send over sensor data
    DEBUG('-> requesting data from ' + c.id)
    checked[checked.length] = c.id
    c.emit('all')
  }
}

io.on('connection', function (socket) {
  DEBUG('-> client connected (' + socket.id + ')')
  clients[socket.id] = {socket: socket, type: undefined}
  socket.emit('identify')

  /* Identification - required to send or recieve data */
  socket.on('identify', function (data) {
    if (data === 'sender') {
      clients[socket.id].type = 'sender'
      console.log('id recv ' + socket.id + ': sender, requesting data')
      requestData(socket)
    } else if (data === 'reciever') {
      clients[socket.id].type = 'reciever'
      console.log('id recv ' + socket.id + ': reciever')
    } else {
      socket.emit('iderror', 'Identity must be "sender" or "reciever."')
    }
  })

  /* Prototype of feedback feature - customize at will */
  socket.on('feedback', function (value) {
    if (clients[socket.id].type === 'sender') {
      if (value) {
        DEBUG('on')
      } else {
        DEBUG('off')
      }
    }
  })

  /* Data is discarded - placeholder for future features */
  socket.on('sensor-data', function (data) {
    if (clients[socket.id].type === 'sender') {
      DEBUG(data)
    }
  })

  /* Data is discarded - placeholder for future features */
  socket.on('node-data', function (data) {
    if (clients[socket.id].type === 'sender') {
      DEBUG(data)
    }
  })

  /* all-data signal
   * Recieves combined node and sensor data, then inserts it into
   * the configured MongoDB collection.
   */
  socket.on('all-data', function (data) {
    if (clients[socket.id].type === 'sender') {
      DEBUG('-> recieved data from ' + data.name)
      DEBUG('   data: ' + JSON.stringify(data))
      dataHandlerCb(data)
    }
  })

  /* sensor-single signal
   * Handler for data from a single sensor. Identical to
   * the all-data signal for now.
   */
  socket.on('sensor-single', function (data) {
    if (clients[socket.id].type === 'sender') {
      DEBUG('-> recieved single sensor from ' + data.name)
      DEBUG('   data: ' + JSON.stringify(data))
      dataHandlerCb(data)
    }
  })

  /* query signal
   * Used by recievers to query the database
   */
  socket.on('query', function (query) {
    if (clients[socket.id].type === 'reciever') {
      MongoClient.connect(config.url, function () {
        assert.equal(null, err)
        collection = db.collection(config.collection)
        collection.find(query, function (err, result) {
          socket.emit('result', result)
          db.close()
        })
      })
    }
  })

  /* disconnect signal
   * Removes a client from the client list
   */
  socket.on('disconnect', function () {
    if (clients[socket.id]) {
      delete clients[socket.id]
    }
  })
})

// Start requesting data at regular intervals
new CronJob('1 * * * * *', function () {
  requestData()
}, null, true, config.timezone)

http.listen(3000, function () {
  console.log('senselog ready')
})
