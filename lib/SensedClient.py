import time
import struct
import socket
import msgpack


DATA_ID = b'\x01\x02'
DATA_REQ = b'\x01\x01'
DATA_ERR = b'\x01\x02'


class SensedClient(object):
    def __init__(self, cfg):
        self.hosts = cfg['hosts']
        self.interval = cfg['interval']

    def run_meta(self):
        print('Meta Process')
        for host in self.hosts:
            print('Pinging {}...'.format(host), end=' ')
            meta = self.get_meta(host)
            print('Metadata recieved: {}'.format(meta))

    def run_forever(self):
        print('Data Process')
        while True:
            self.run_once()
            time.sleep(self.interval)

    def run_once(self):
        for host in self.hosts:
            print('Pinging {}...'.format(host), end=' ')
            data = self.get_data(host)
            print('Recieved data: {}'.format(data))

    def get_meta(self, host):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(DATA_ID, host)

        raw_meta = s.recv(1024)
        meta = msgpack.unpackb(raw_meta)

        return meta

    def get_sensors(self, host):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(DATA_REQ, host)

        raw_size, addr = s.recv(4)
        size = struct.unpack('I', raw_size)

        raw_data, addr = s.recv(size)
        header = data[:2]
        data = msgpack.unpackb(data[2:])

        return {'header': header, 'data': data}
