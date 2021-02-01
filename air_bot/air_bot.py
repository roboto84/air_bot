# Air data sender
import os
import sys
import time
import logging.config
from threading import Thread
from typing import Any, NoReturn, List
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from client_network import ClientNetwork


class AirBot:
    def __init__(self, logging_object: Any, data_interval: int, data_file: str, socket_host: str, socket_port: int):
        self.logger: Any = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.data_interval: int = data_interval
        self.data_file: str = data_file
        self.socket_host: str = socket_host
        self.socket_port: int = socket_port
        self.receive_thread: Any = None
        self.socket_network: ClientNetwork = ClientNetwork(logging, self.socket_host, self.socket_port,
                                                           'air_bot', 'app')

    def thread_it(self, socket_receive):
        self.receive_thread: Any = Thread(target=socket_receive)
        self.receive_thread.start()

    def run_job(self) -> NoReturn:
        try:
            scheduler: BlockingScheduler = BlockingScheduler()
            scheduler.add_job(self.send_air_data, 'interval', seconds=self.data_interval)
            scheduler.start()
        except KeyboardInterrupt:
            self.logger.warning('Received a KeyboardInterrupt... exiting process')
            sys.exit()

    def send_air_data(self) -> NoReturn:
        data: str = self.get_data(self.data_file).strip()
        data_array: List[str] = data.split(',')
        message: dict = {
            'air_pressure': data_array[0],
            'dateTime': data_array[1]
        }
        self.socket_network.sock_it()
        self.thread_it(self.socket_network.receive)
        time.sleep(1)
        self.logger.info(f'Sending: {message}')
        self.socket_network.send_message(str(message))
        self.socket_network.close_it()

    @staticmethod
    def get_data(file_address: str) -> str:
        with open(file_address, 'r') as data:
            num_lines: int = sum(1 for line in data)

        with open(file_address, 'r') as infile:
            lines: List[str] = infile.readlines()

        for pos, line in enumerate(lines):
            if pos == num_lines-1:
                return line


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        SEND_DATA_INTERVAL: int = int(os.getenv('SEND_DATA_INTERVAL'))
        DATA_FILE: str = os.getenv('DATA_FILE')
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))

        print('\nBarometric data sender will run every {}:'.format(SEND_DATA_INTERVAL))
        air_collect = AirBot(logging, SEND_DATA_INTERVAL, DATA_FILE, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT)
        air_collect.run_job()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
