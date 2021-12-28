# Air data sender
import os
import sys
import time
import logging.config
from threading import Thread
from typing import Any, NoReturn, List
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from wh00t_core.library.client_network import ClientNetwork
from air_core.library.air import Air
from air_core.library.air_settings import TIMEZONE


class AirBot:
    def __init__(self, logging_object: Any, data_interval: int, live_file: str, forecast_file: str, socket_host: str,
                 socket_port: int):
        self.logger: Any = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.data_interval: int = data_interval
        self.live_file: str = live_file
        self.forecast_file: str = forecast_file
        self.socket_host: str = socket_host
        self.socket_port: int = socket_port
        self.receive_thread: Any = None
        self.socket_network: ClientNetwork = ClientNetwork(self.socket_host, self.socket_port,
                                                           'air_bot', 'app', logging)

    def __thread_it(self, socket_receive):
        self.receive_thread: Any = Thread(target=socket_receive)
        self.receive_thread.start()

    def run_job(self) -> NoReturn:
        try:
            start_time = '2020-10-10 03:05:00'
            self.__send_current_data()
            time.sleep(10)
            self.__send_daily_air_data()
            scheduler: BlockingScheduler = BlockingScheduler(timezone=TIMEZONE)
            scheduler.add_job(self.__send_current_data, 'interval', start_date=start_time, seconds=self.data_interval)
            scheduler.add_job(self.__send_daily_air_data, 'cron', day_of_week='*', hour=0, minute='10')
            scheduler.start()

        except KeyboardInterrupt:
            self.logger.warning('Received a KeyboardInterrupt... exiting process')
            sys.exit()

    def __send_current_data(self) -> NoReturn:
        data: str = self.get_data('current', self.live_file)[0].strip()
        self.__send_weather_data(self.structure_data(data), ['air_weather', 'air_pollution', 'air_pollen'])

    def __send_daily_air_data(self) -> NoReturn:
        data: List[str] = self.get_data('daily', self.forecast_file)
        for forecast in data:
            self.__send_weather_data(self.structure_data(forecast.strip()),
                                     ['air_weather_forecast', 'air_pollution_forecast', 'air_pollen_forecast'])
            time.sleep(5)

    def __send_weather_data(self, weather: Air, weather_array_categories: List[str]) -> NoReturn:
        weather_array: List[dict] = [weather.get_basic_weather(), weather.get_pollution(), weather.get_pollen()]
        self.socket_network.sock_it()
        self.__thread_it(self.socket_network.receive)

        for index, weather_portion in enumerate(weather_array):
            time.sleep(2)
            self.logger.info(f'Sending {weather_array_categories[index]}: {weather_portion}')
            self.socket_network.send_message(weather_array_categories[index], str(weather_portion))
        self.socket_network.close_it()

    @staticmethod
    def structure_data(data: str) -> Air:
        data_array: List[str] = data.split(',')
        new_air = Air('imperial')
        new_air.set_weather_with_array(data_array)
        return new_air

    @staticmethod
    def get_data(data_type: str, file_address: str) -> List[str]:
        with open(file_address, 'r') as data:
            num_lines: int = sum(1 for line in data)

        with open(file_address, 'r') as infile:
            lines: List[str] = infile.readlines()

        if data_type == 'daily':
            return lines[1:]
        else:
            for pos, line in enumerate(lines):
                if pos == num_lines - 1:
                    return [line]


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        SEND_DATA_INTERVAL: int = int(os.getenv('SEND_DATA_INTERVAL'))
        LIVE_FILE: str = os.getenv('LIVE_DATA_FILE')
        FORECAST_FILE: str = os.getenv('FORECAST_DATA_FILE')
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))

        print(f'\nBarometric data sender will run every {SEND_DATA_INTERVAL} seconds:')
        air_bot = AirBot(logging, SEND_DATA_INTERVAL, LIVE_FILE, FORECAST_FILE, HOST_SERVER_ADDRESS,
                         SOCKET_SERVER_PORT)
        air_bot.run_job()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
