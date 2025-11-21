import select
from socket import *
import threading
import sys


class ServerTCP:
    def __init__(self, server_port):
        self.server_port = server_port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        addr = gethostbyname(gethostname())
        self.server_socket.bind((addr, server_port))
        self.server_socket.listen()
        self.clients = {}
        self.run_event = threading.Event()
        self.handle_event = threading.Event()
        self.run_event.clear()
        self.handle_event.clear()

    def accept_client(self):
        try:
            readability, _, _ = select.select([self.server_socket], [], [], 0.5)
            if not readability:
                return False

            # accept connection
            client_socket, client_addr = self.server_socket.accept()

            # get client name
            name_bytes = client_socket.recv(1024)
            if not name_bytes:
                client_socket.close()
                return False

            client_name = name_bytes.decode().strip()

            # check if name is used
            if client_name in self.clients.values():
                try:
                    client_socket.sendall(b"Name already taken")
                finally:
                    client_socket.close()
                return False

            # name unique: welcome client
            client_socket.sendall(b"Welcome")
            self.clients[client_socket] = client_name
            # announce user joining
            self.broadcast(client_socket, "join")

            return True

        except Exception:
            return False

    def close_client(self, client_socket):
        try:
            if client_socket not in self.clients:
                try:
                    client_socket.close()
                except:
                    pass
                return False

            # find client name
            client_name = self.clients[client_socket]

            if client_name:    # announce they left
                self.broadcast(client_socket, "exit")

            del self.clients[client_socket]

            try:    # close their socket
                client_socket.close()
            except:
                return False

            return True

        except Exception as e:
            return False

    def broadcast(self, client_socket_sent, message):
        try:
            sender_name = self.clients.get(client_socket_sent)

            if sender_name is None:
                return

            # format message
            if message == "join":
                f_msg = f"User {sender_name} joined"
            elif message == "exit":
                f_msg = f"User {sender_name} left"
            else:
                f_msg = f"{sender_name}: {message}"

            encoded = f_msg.encode()

            # send to clients
            for sock, name in list(self.clients.items()):
                if sock is client_socket_sent:
                    continue
                try:
                    sock.sendall(encoded)
                except:
                    self.close_client(sock)

        except Exception:
            pass

    def shutdown(self):
        try:
            # send server shutdown message to clients
            msg = b"server-shutdown"
            for sock in list(self.clients.keys()):
                try:
                    sock.sendall(msg)
                except:
                    pass
                self.close_client(sock)

            # set run and handle events
            if hasattr(self, "run_event"):
                self.run_event.set()
            if hasattr(self, "handle_event"):
                self.handle_event.set()

            try:
                self.server_socket.close()
            except:
                pass

        except Exception:
            pass

    def get_clients_number(self):
        return len(self.clients)

    def handle_client(self, client_socket):
        while not self.handle_event.is_set():
            try:
                readability, _, _ = select.select([client_socket], [], [], 0.5)
                if not readability:
                    continue

                data = client_socket.recv(1024)

                if not data:
                    self.close_client(client_socket)
                    break

                message = data.decode().strip()

                if message == "exit":
                    self.close_client(client_socket)
                    break

                self.broadcast(client_socket, message)

            except (ConnectionResetError, ConnectionAbortedError):
                self.close_client(client_socket)
                break
            except Exception:
                self.close_client(client_socket)
                break

    def run(self):
        if hasattr(self, "run_event"):
            self.run_event.clear()
        if hasattr(self, "handle_event"):
            self.handle_event.clear()

        print("Server started. Press Ctrl+C to stop.")

        try:
            while not self.run_event.is_set():
                before = set(self.clients.keys())

                accepted = self.accept_client()

                if accepted:
                    after = set(self.clients.keys())
                    new_socket = after - before

                    for client_socket in new_socket:
                        t = threading.Thread(
                            target=self.handle_client,
                            args=(client_socket,),
                            daemon=True
                        )
                        t.start()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: shutting down server...")
        finally:
            if hasattr(self, "run_event"):
                self.run_event.set()
            if hasattr(self, "handle_event"):
                self.handle_event.set()

            self.shutdown()


class ClientTCP:
    def __init__(self, client_name, server_port):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.server_addr = gethostbyname(gethostname())
        self.server_port = server_port
        self.client_name = client_name
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event()

    def connect_server(self):
        try:
            self.client_socket.connect((self.server_addr, self.server_port))
            # send name to server
            self.client_socket.sendall(self.client_name.encode())
            # wait for reply from server
            response = self.client_socket.recv(1024)
            if not response:
                print("No response from server.")
                return False

            msg = response.decode().strip()

            if "Welcome" in msg:
                print(msg)
                return True
            else:
                print(msg)
                return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send(self, text):
        try:
            self.client_socket.sendall(text.encode())
        except Exception as e:
            print(f"Send error: {e}")
            self.exit_run.set()
            self.exit_receive.set()

    def receive(self):
        while not self.exit_receive.is_set():
            try:
                readability, _, _ = select.select([self.client_socket], [], [], 0.5)
                if not readability:
                    continue

                data = self.client_socket.recv(1024)
                if not data:
                    print("Server closed the connection")
                    self.exit_run.set()
                    break

                msg = data.decode().strip()
                if msg == "server-shutdown":
                    print("Server is shutting down.")
                    self.exit_run.set()
                    break

                print(msg)
            except (ConnectionResetError, ConnectionAbortedError):
                print("Connection lost.")
                self.exit_run.set()
                break
            except Exception as e:
                print(f"Receive error: {e}")
                self.exit_run.set()
                break

        self.exit_receive.set()

    def run(self):
        if not self.connect_server():
            try:
                self.client_socket.close()
            except:
                pass
            return

        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

        try:
            while not self.exit_run.is_set():
                try:
                    user_input = input()
                except EOFError:
                    user_input = "exit"
                except KeyboardInterrupt:
                    user_input = "exit"

                user_input = user_input.strip()

                if user_input == "exit":
                    self.send("exit")
                    self.exit_run.set()
                    self.exit_receive.set()
                    break
                else:
                    self.send(user_input)
        finally:
            try:
                self.client_socket.close()
            except:
                pass
            self.exit_run.set()
            self.exit_receive.set()


class ServerUDP:
    def __init__(self, server_port):
        pass
    def accept_client(self, client_addr, message):
        pass
    def close_client(self, client_addr):
        pass
    def broadcast(self):
        pass
    def shutdown(self):
        pass
    def get_clients_number(self):
        pass
    def run(self):
        pass


class ClientUDP:
    def __init__(self, client_name, server_port):
        pass
    def connect_server(self):
        pass
    def send(self, text):
        pass
    def receive(self):
        pass
    def run(self):
        pass