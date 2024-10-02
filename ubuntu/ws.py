import socket
import threading
import select
import signal
import sys
import time
import getopt

# Listen
LISTENING_ADDR = '127.0.0.1'
LISTENING_PORT = 10015
PASSWORD = ''  # Password for authentication, if needed

# Constants
BUFFER_SIZE = 4096 * 4
TIMEOUT = 60
DEFAULT_HOST = '127.0.0.1:143'

# Custom response instead of the default Switching Protocol response
CUSTOM_RESPONSE = (
    'HTTP/1.1 101 <b><font color="#22f619">𝐍𝐄𝐓 𝐁𝐘 𝐂𝐇𝐀𝐏𝐄𝐄𝐘</font></b>\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Accept: foo\r\n\r\n'
)

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.running = False
        self.host = host
        self.port = port
        self.connections = []
        self.connections_lock = threading.Lock()
        self.log_lock = threading.Lock()

    def run(self):
        with socket.socket(socket.AF_INET) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.settimeout(2)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)  # Allow a backlog of 5 connections
            self.running = True

            try:
                while self.running:
                    try:
                        client_socket, address = server_socket.accept()
                        client_socket.setblocking(1)
                        connection_handler = ConnectionHandler(client_socket, self, address)
                        connection_handler.start()
                        self.add_connection(connection_handler)
                    except socket.timeout:
                        continue
            finally:
                self.running = False

    def log(self, message):
        with self.log_lock:
            print(message)

    def add_connection(self, connection):
        with self.connections_lock:
            if self.running:
                self.connections.append(connection)

    def remove_connection(self, connection):
        with self.connections_lock:
            self.connections.remove(connection)

    def close(self):
        self.running = False
        with self.connections_lock:
            for conn in list(self.connections):
                conn.close()


class ConnectionHandler(threading.Thread):
    def __init__(self, client_socket, server, address):
        super().__init__()
        self.client_closed = False
        self.target_closed = True
        self.client_socket = client_socket
        self.server = server
        self.address = address
        self.log_message = f'Connection from {address}'

    def close(self):
        if not self.client_closed:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except Exception as e:
                self.server.log(f'Error closing client socket: {e}')
            finally:
                self.client_closed = True

    def run(self):
        try:
            self.client_buffer = self.client_socket.recv(BUFFER_SIZE)
            host_port = self.find_header(self.client_buffer, 'X-Real-Host') or DEFAULT_HOST
            password = self.find_header(self.client_buffer, 'X-Pass')

            if PASSWORD and password != PASSWORD:
                self.client_socket.sendall(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
                return

            if host_port.startswith(('127.0.0.1', 'localhost')):
                self.connect_to_target(host_port)
            else:
                self.client_socket.sendall(b'HTTP/1.1 403 Forbidden!\r\n\r\n')

        except Exception as e:
            self.log_message += f' - error: {str(e)}'
            self.server.log(self.log_message)
        finally:
            self.close()
            self.server.remove_connection(self)

    def find_header(self, headers, header):
        header_index = headers.find(header + ': ')
        if header_index == -1:
            return ''

        header_index += len(header) + 2  # Move past the header and ': '
        end_index = headers.find('\r\n', header_index)
        return headers[header_index:end_index] if end_index != -1 else ''

    def connect_to_target(self, host):
        host, port = (host.split(':') + [443])[:2]  # Default port for HTTPS
        port = int(port)

        try:
            address_info = socket.getaddrinfo(host, port)[0]
            self.target_socket = socket.socket(address_info[0], address_info[1], address_info[2])
            self.target_closed = False
            self.target_socket.connect(address_info[4])
            self.client_socket.sendall(CUSTOM_RESPONSE.encode())  # Send the custom response
            self.handle_communication()
        except Exception as e:
            self.server.log(f'Error connecting to target {host}:{port} - {e}')
            self.client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')

    def handle_communication(self):
        sockets = [self.client_socket, self.target_socket]
        count = 0
        error_occurred = False

        while True:
            count += 1
            read_sockets, _, error_sockets = select.select(sockets, [], sockets, 3)
            if error_sockets:
                error_occurred = True
            if read_sockets:
                for sock in read_sockets:
                    try:
                        data = sock.recv(BUFFER_SIZE)
                        if data:
                            if sock is self.target_socket:
                                self.client_socket.send(data)
                            else:
                                while data:
                                    bytes_sent = self.target_socket.send(data)
                                    data = data[bytes_sent:]
                            count = 0  # Reset timeout counter
                        else:
                            break
                    except Exception:
                        error_occurred = True
                        break
            if count == TIMEOUT or error_occurred:
                break

    def close(self):
        super().close()
        if not self.target_closed:
            try:
                self.target_socket.shutdown(socket.SHUT_RDWR)
                self.target_socket.close()
            except Exception as e:
                self.server.log(f'Error closing target socket: {e}')
            finally:
                self.target_closed = True


def print_usage():
    print('Usage: proxy.py -p <port>')
    print('       proxy.py -b <bindAddr> -p <port>')
    print('       proxy.py -b 0.0.0.0 -p 80')


def parse_args(argv):
    global LISTENING_ADDR
    global LISTENING_PORT

    try:
        opts, args = getopt.getopt(argv, "hb:p:", ["bind=", "port="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)


def signal_handler(sig, frame):
    print('Stopping server...')
    server.close()
    sys.exit(0)


def main():
    global server
    parse_args(sys.argv[1:])
    print("\n:-------PythonProxy-------:\n")
    print(f"Listening addr: {LISTENING_ADDR}")
    print(f"Listening port: {LISTENING_PORT}\n")
    print(":-------------------------:\n")
    
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping server...')
        server.close()


if __name__ == '__main__':
    main()
