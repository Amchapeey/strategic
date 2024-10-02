import socket
import threading
import select
import sys
import time
import getopt
import base64
import hashlib

# Listen
LISTENING_ADDR = '127.0.0.1'
if sys.argv[1:]:
    LISTENING_PORT = sys.argv[1]
else:
    LISTENING_PORT = 10015  
# Passwd
PASS = ''

# CONST
BUFLEN = 4096 * 4
TIMEOUT = 60
DEFAULT_HOST = '127.0.0.1:143'
RESPONSE_TEMPLATE = 'HTTP/1.1 101 <b><font color="#22f619">𝐍𝐄𝐓 𝐁𝐘 𝐂𝐇𝐀𝐏𝐄𝐄𝐘</font></b>\r\n' \
                    'Upgrade: websocket\r\n' \
                    'Connection: Upgrade\r\n' \
                    'Sec-WebSocket-Accept: {}\r\n\r\n'

class Server(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.running = False
        self.host = host
        self.port = port
        self.threads = []
        self.threadsLock = threading.Lock()
        self.logLock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        intport = int(self.port)
        self.soc.bind((self.host, intport))
        self.soc.listen(0)
        self.running = True

        try:
            while self.running:
                try:
                    c, addr = self.soc.accept()
                    c.setblocking(1)
                except socket.timeout:
                    continue

                conn = ConnectionHandler(c, self, addr)
                conn.start()
                self.addConn(conn)
        finally:
            self.running = False
            self.soc.close()

    def printLog(self, log):
        self.logLock.acquire()
        print(log)
        self.logLock.release()

    def addConn(self, conn):
        try:
            self.threadsLock.acquire()
            if self.running:
                self.threads.append(conn)
        finally:
            self.threadsLock.release()

    def removeConn(self, conn):
        try:
            self.threadsLock.acquire()
            self.threads.remove(conn)
        finally:
            self.threadsLock.release()

    def close(self):
        try:
            self.running = False
            self.threadsLock.acquire()

            threads = list(self.threads)
            for c in threads:
                c.close()
        finally:
            self.threadsLock.release()


class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        threading.Thread.__init__(self)
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = ''
        self.server = server
        self.log = 'Connection: ' + str(addr)

    def close(self):
        try:
            if not self.clientClosed:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")
        finally:
            self.clientClosed = True

        try:
            if not self.targetClosed:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
        except Exception as e:
            print(f"Error closing target socket: {e}")
        finally:
            self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)

            # Extract the Sec-WebSocket-Key from the request
            websocket_key = self.findHeader(self.client_buffer.decode(), 'Sec-WebSocket-Key')

            if websocket_key:
                # Generate the Sec-WebSocket-Accept value
                accept_value = self.generate_accept_value(websocket_key)

                # Send the response to upgrade the connection
                response = RESPONSE_TEMPLATE.format(accept_value)
                self.client.sendall(response.encode('utf-8'))

                # Further connection handling...
                hostPort = self.findHeader(self.client_buffer.decode(), 'X-Real-Host')

                if hostPort == '':
                    hostPort = DEFAULT_HOST

                split = self.findHeader(self.client_buffer.decode(), 'X-Split')

                if split != '':
                    self.client.recv(BUFLEN)

                if hostPort != '':
                    passwd = self.findHeader(self.client_buffer.decode(), 'X-Pass')

                    if len(PASS) != 0 and passwd == PASS:
                        self.method_CONNECT(hostPort)
                    elif len(PASS) != 0 and passwd != PASS:
                        self.client.send('HTTP/1.1 400 WrongPass!\r\n\r\n'.encode('utf-8'))
                    elif hostPort.startswith('127.0.0.1') or hostPort.startswith('localhost'):
                        self.method_CONNECT(hostPort)
                    else:
                        self.client.send('HTTP/1.1 403 Forbidden!\r\n\r\n'.encode('utf-8'))
                else:
                    print('- No X-Real-Host!')
                    self.client.send('HTTP/1.1 400 NoXRealHost!\r\n\r\n'.encode('utf-8'))

            else:
                self.client.send('HTTP/1.1 400 Bad Request\r\n\r\n'.encode('utf-8'))

        except Exception as e:
            self.log += ' - error: ' + str(e)
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def findHeader(self, head, header):
        aux = head.find(header + ': ')

        if aux == -1:
            return ''

        aux = head.find(':', aux)
        head = head[aux + 2:]
        aux = head.find('\r\n')

        if aux == -1:
            return ''

        return head[:aux]

    def generate_accept_value(self, websocket_key):
        # Concatenate the key with the magic string
        combined_key = websocket_key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        
        # Generate the SHA-1 hash
        sha1_hash = hashlib.sha1(combined_key.encode('utf-8')).digest()
        
        # Return the base64-encoded hash
        return base64.b64encode(sha1_hash).decode('utf-8')

    def connect_target(self, host):
        i = host.find(':')
        if i != -1:
            port = int(host[i + 1:])
            host = host[:i]
        else:
            if self.method == 'CONNECT':
                port = 443
            else:
                port = sys.argv[1]

        (soc_family, soc_type, proto, _, address) = socket.getaddrinfo(host, port)[0]

        self.target = socket.socket(soc_family, soc_type, proto)
        self.targetClosed = False
        self.target.connect(address)

    def method_CONNECT(self, path):
        self.log += ' - CONNECT ' + path

        self.connect_target(path)
        self.client.sendall(RESPONSE_TEMPLATE.encode('utf-8'))
        self.client_buffer = ''

        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        error = False
        while True:
            count += 1
            (recv, _, err) = select.select(socs, [], socs, 3)
            if err:
                error = True
            if recv:
                for in_ in recv:
                    try:
                        data = in_.recv(BUFLEN)
                        if data:
                            if in_ is self.target:
                                self.client.send(data)
                            else:
                                while data:
                                    byte = self.target.send(data)
                                    data = data[byte:]

                            count = 0
                        else:
                            break
                    except Exception as e:
                        print(f"Error during data transfer: {e}")
                        error = True
                        break
            if count == TIMEOUT:
                error = True
            if error:
                break


def print_usage():
    print('Usage: ws.py -p <port>')
    print('       ws.py -b <bindAddr> -p <port>')
    print('       ws.py -b 0.0.0.0 -p 80')

def parse_args(argv):
    global LISTENING_ADDR
    global LISTENING_PORT
    
    try:
        opts, args = getopt.getopt(argv,"hb:p:",["bind=","port="])
    except getopt.GetoptError:
        print_usage()
        sys
