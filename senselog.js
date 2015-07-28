var http = require('http').Server(null);
var io = require('socket.io').Server(http);
var config = require('./config/config.json');

var mongo = require('mongo-client');
var insert = require('mongo-client/insert');

var mclient = mongo(config.mongourl);
var collection = mclient(config.collection);

var clients = [];

io.on('connection', function(socket) {

    console.log('-> client connected');
    clients[clients.length] = socket;

    /* Prototype of feedback feature - customize at will */
    socket.on('feedback', function(value) {
        if (value) {
            console.log('<- pressed');
            socket.emit('sensors');
        } else {
            console.log('<- released');
        }
    });

    /* Data is discarded - placeholder for future features */
    socket.on('sensor-data', function(data) {
        console.log(data);
    });

    /* Data is discarded - placeholder for future features */
    socket.on('node-data', function(data) {
        console.log(data);
    });

    /* all-data signal
     * Recieves combined node and sensor data, then inserts it into
     * the configured MongoDB collection.
     */
    socket.on('all-data', function(data) {
        console.log('<- recieved data from ' + socket.id);
        insert(collection, data);
    });


    /* disconnect signal
     * Removes a client from the client list
     */
    socket.on('disconnect', function() {
        var index = clients.indexOf(socket);
        if (index > -1) {
            clients.splice(index, 1);
            console.log('<- client disconnected');
        }
    });
});

http.listen(3000, function() {
    console.log('ready');
});
