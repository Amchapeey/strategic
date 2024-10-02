import socket, threading, select, sys, time, getopt, signal
from datetime import datetime

# Constants
BUFLEN = 4096 * 4
TIMEOUT = 60
DEFAULT_HOST = '127.0.0.1:143'
RESPONSE = ('HTTP/1.1 101 <b><font color="#22f619">𝐍𝐄𝐓 𝐁𝐘 𝐂𝐇𝐀𝐏𝐄𝐄𝐘</font></b>\r\n'
            'Upgrade: websocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Accept: foo\r\n\r\n')
PASS = ''  # Empty means no password required

# Default listening address and port
LISTENING_ADDR = '127.0.0.1'
LISTENING_PORT = 10015

# Logging function with timestamp
def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.running = False
        self.host = host
        self.port = port
        self.threads = []
        self.threads_lock = threading.Lock()
        self.log_lock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        self.soc.bind((self.host, int(self.port)))
        self.soc.listen(5)
        self.running = True
        log_message(f"Server started on {self.host}:{self.port}")

        try:
            while self.running:
                try:
                    client_socket, addr = self.soc.accept()
                    client_socket.setblocking(1)
                    log_message(f"Accepted connection from {addr}")
                except socket.timeout:
                    continue

                conn_handler = ConnectionHandler(client_socket, self, addr)
                conn_handler.start()
                self.add_conn(conn_handler)
        finally:
            self.running = False
            self.soc.close()

    def add_conn(self, conn):
        with self.threads_lock:
            if self.running:
                self.threads.append(conn)

    def remove_conn(self, conn):
        with self.threads_lock:
            self.threads.remove(conn)

    def close(self):
        log_message("Shutting down server...")
        with self.threads_lock:
            self.running = False
            for conn in self.threads:
                conn.close()
        self.soc.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, client_socket, server, addr):
        super().__init__()
        self.client_socket = client_socket
        self.server = server
        self.addr = addr
        self.client_closed = False
        self.target_closed = True
        self.client_buffer = ''

    def close(self):
        try:
            if not self.client_closed:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
        except:
            pass
        finally:
            self.client_closed = True

        try:
            if not self.target_closed:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
        except:
            pass
        finally:
            self.target_closed = True

    def run(self):
        try:
            self.client_buffer = self.client_socket.recv(BUFLEN)
            host_port = self.find_header(self.client_buffer, 'X-Real-Host')

            if host_port == '':
                host_port = DEFAULT_HOST

            split = self.find_header(self.client_buffer, 'X-Split')
            if split != '':
                self.client_socket.recv(BUFLEN)

            if host_port:
                passwd = self.find_header(self.client_buffer, 'X-Pass')
                if PASS and passwd == PASS:
                    self.method_connect(host_port)
                elif PASS and passwd != PASS:
                    self.client_socket.send(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
                elif host_port.startswith('127.0.0.1') or host_port.startswith('localhost'):
                    self.method_connect(host_port)
                else:
                    self.client_socket.send(b'HTTP/1.1 403 Forbidden!\r\n\r\n')
            else:
                log_message('No X-Real-Host header found.')
                self.client_socket.send(b'HTTP/1.1 400 NoXRealHost!\r\n\r\n')

        except Exception as e:
            log_message(f"Error: {e}")
        finally:
            self.close()
            self.server.remove_conn(self)

    def find_header(self, buffer, header_name):
        try:
            header_start = buffer.find(f'{header_name}: '.encode())
            if header_start == -1:
                return ''
            header_end = buffer.find(b'\r\n', header_start)
            return buffer[header_start + len(header_name) + 2:header_end].decode()
        except Exception as e:
            log_message(f"Error finding header {header_name}: {e}")
            return ''

    def connect_target(self, host):
        try:
            host, port = host.split(':')
            port = int(port)
            self.target = socket.create_connection((host, port))
            self.target_closed = False
        except Exception as e:
            log_message(f"Error connecting to target {host}: {e}")
            self.target_closed = True

    def method_connect(self, host_port):
        log_message(f"Connecting to {host_port} via CONNECT method")
        self.connect_target(host_port)
        if not self.target_closed:
            self.client_socket.sendall(RESPONSE.encode())
            self.client_buffer = ''
            self.forward_data()

    def forward_data(self):
        sockets = [self.client_socket, self.target]
        while True:
            try:
                readable, _, errors = select.select(sockets, [], sockets, TIMEOUT)
                if errors:
                    break
                for sock in readable:
                    data = sock.recv(BUFLEN)
                    if sock is self.target:
                        self.client_socket.sendall(data)
                    else:
                        self.target.sendall(data)
            except Exception as e:
                log_message(f"Error during data forwarding: {e}")
                break
        self.close()

def parse_args():
    global LISTENING_ADDR, LISTENING_PORT
    opts, args = getopt.getopt(sys.argv[1:], "b:p:", ["bind=", "port="])
    for opt, arg in opts:
        if opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)

def main():
    parse_args()
    log_message(f"Starting WebSocket Proxy on {LISTENING_ADDR}:{LISTENING_PORT}")
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("Received shutdown signal")
        server.close()

if __name__ == "__main__":
    main()
