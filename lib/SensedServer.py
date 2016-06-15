import msgpack
import socketserver


DATA_ID = '\x01\x02'
DATA_REQ = '\x01\x01'


class SenseLogClient(socketserver.BaseRequestHandler):
    def handle(self):
        r_data = self.request[0].strip()
        # socket = self.request[1]

        data = msgpack.unpackb(r_data)

        print('Sensor data recieved: {}'.format(data))
