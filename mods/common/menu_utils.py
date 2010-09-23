import cPickle
import socket
import struct
import select

marshall = cPickle.dumps
unmarshall = cPickle.loads

def send(channel, *args):
    buf = marshall(args)
    value = socket.htonl(len(buf))
    size = struct.pack("L",value)
    channel.send(size)
    channel.send(buf)

def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        return ''
    buf = ""
    while len(buf) < size:
        buf = channel.recv(size - len(buf))
    return unmarshall(buf)[0]

HOST = 'localhost'
PORT = 8888

class ScriptServer:
    def __init__(self, port = PORT, backlog = 5):
        self.scriptmap = {}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', port))
        print 'Listening to port', port, '...'
        self.server.listen(backlog)
        self.inputs = [self.server]

    def read_data(self):
        self.outputs = []
        try:
            inputready, outputready, exceptready = select.select(self.inputs, self.outputs, [], 0)
        except select.error, e:
            print 'ScriptServer select error'
            return None
        except socket.error, e:
            print 'ScriptServer socket error'
            return None
        for s in inputready:
            if s == self.server:
                # this is a new connection
                client, address = self.server.accept()
                print 'ScriptServer got connection %d from %s' % (client.fileno(), address)
                self.scriptmap[client] = address
                self.outputs.append(client)
                self.inputs.append(client)
            else:
                # this is a message on an existing connection
                try:
                    data = receive(s)
                    if data:
                        return data
                    else:
                        print 'ScriptServer: %d hung up' % s.fileno()
                        s.close()
                        self.inputs.remove(s)
                        self.outputs.remove(s)
                except socket.error, e:
                    print 'ScriptServer socket error'
                    self.inputs.remove(e)
                    self.outputs.remove(e)
        return None

class ScriptClient:
    def __init__(self, host = HOST, port = PORT):
        self.host = host
        self.port = port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print 'ScriptClient connected to ScriptServer at (%s, %d)' % (self.host, self.port)
        except socket.error, e:
            print 'ScriptClient could not connect to ScriptServer'
    def send(self, data):
        if data and self.sock:
            send(self.sock, data)
