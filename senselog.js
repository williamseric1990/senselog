var http = require('http').Server(null);
var io = require('socket.io').Server(http);
var MongoClient = require('mongodb').MongoClient;
var config = require('./config/config.json');

io.on('connection', function(socket) {

    console.log('-> client connected');

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
        MongoClient.connect(config.mongourl, function(err, db) {
            var collection = db.collection(config.collection);
            collection.insert(data);
            db.close();
        });
    });

});

http.listen(3000, function() {
    console.log('ready');
});