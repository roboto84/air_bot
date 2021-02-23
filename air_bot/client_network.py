# Socket Client Network base class

import os
import time
from datetime import datetime
from typing import List, Any, NoReturn
from socket import AF_INET, socket, SOCK_STREAM


class ClientNetwork:
    BUFFER_SIZE: int = 1024
    message_history: List[str] = []

    def __init__(self, logging_object: Any, host: str, port: int, app_id: str, app_profile: str) -> NoReturn:
        self.logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging_object.INFO)

        self.number_of_messages: int = 0
        self.client_socket: Any = None
        self.client_socket_error: bool = False
        self.address: tuple = (host, port)
        self.app_id: str = app_id
        self.app_profile: str = app_profile

    def sock_it(self) -> NoReturn:
        try:
            self.logger.info(f'Attempting socket connection to {self.address}')
            self.client_socket: Any = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.address)
            package: str = self.package_data(self.app_id, self.app_profile, 'air_bot_connect', '')
            self.client_socket.send(bytes(package, 'utf8'))
            self.logger.info(f'Connection to {self.address} has succeeded')
        except ConnectionRefusedError as connection_refused_error:
            self.logger.error(f'Received ConnectionRefusedError: {(str(connection_refused_error))}')
            os._exit(1)
        except OSError as os_error:  # Possibly client has left the chat.
            self.logger.error(f'Received an OSError: {(str(os_error))}')
            os._exit(1)

    def send_message(self, message_category: str, message: str) -> NoReturn:
        if self.client_socket_error:
            os._exit(1)
        else:
            try:
                packaged_message: str = self.package_data(self.app_id, self.app_profile, message_category, message)
                self.client_socket.send(bytes(packaged_message, 'utf8'))
            except IOError as io_error:
                self.logger.error(f'Received IOError: {(str(io_error))}')
                self.client_socket_error = True

    def receive(self) -> NoReturn:
        while self.client_socket:
            try:
                message: str = self.client_socket.recv(self.BUFFER_SIZE).decode('utf8', errors='replace').lstrip()
                self.number_of_messages += 1
                self.message_history.append(message)
                print(f'received message: {message}')
            except OSError as os_error:  # Possibly client has left the chat.
                self.logger.error(f'Received OSError: {(str(os_error))}')
                break
            except KeyboardInterrupt:
                self.logger.warning('Received a KeyboardInterrupt... now exiting')
                self.client_socket.close()
                os._exit(1)

    def close_it(self) -> NoReturn:
        time.sleep(0.25)
        self.send_message('air_bot_disconnect', '/exit')
        self.client_socket.close()
        self.client_socket = None

    def get_message_history(self) -> List[str]:
        self.trim_message_history()
        return self.message_history

    def trim_message_history(self) -> NoReturn:
        if len(self.message_history) > 10:
            self.message_history.pop(0)

    @staticmethod
    def package_data(client_id: str, client_profile: str, message_category: str, message: str) -> str:
        data_dict: dict = {
            'id': client_id,
            'profile': client_profile,
            'time': datetime.fromtimestamp(time.time()).strftime('%m/%d %H:%M'),
            'category': message_category,
            'message': message
        }
        return str(data_dict)
