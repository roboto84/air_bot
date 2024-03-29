# Air chat bot
import os
import logging.config
from typing import Any
from dotenv import load_dotenv
from air_bot_utils import AirBotUtils
from wh00t_core.library.client_network import ClientNetwork
from wh00t_core.library.network_commons import NetworkCommons
from air_core.library.air_db import AirDb


class AirBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, sql_lite_db_path: str, timezone: str):
        self._logger: Any = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key = '/air'
        self._current_weather_key = 'current'
        self._weather_forecast_key = 'forecast'
        self._timezone = timezone
        self._air_db: AirDb = AirDb(logging_object, sql_lite_db_path)
        self._network_commons: NetworkCommons = NetworkCommons()
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port, 'air_bot', 'app', logging)

    def run_bot(self) -> None:
        try:
            self._socket_network.sock_it()
            self._socket_network.receive(self._receive_message_callback)
        except TypeError as run_type_error:
            logger.error(f'Received TypeError: {run_type_error}')
            exit()
        except KeyboardInterrupt:
            self._logger.info('Received a KeyboardInterrupt... closing bot')
            exit()

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'air_bot']) and ('message' in package):
            if 'category' in package and \
                    package['category'] == self._network_commons.get_chat_message_category() and \
                    isinstance(package['message'], str) and \
                    self._chat_key in package['message'] and \
                    package['message'].find(self._chat_key) == 0:
                air_command = package['message'].replace(self._chat_key, '')
                if self._current_weather_key in air_command and \
                        air_command.replace(self._current_weather_key, '') == ' ':
                    self._send_chat_weather(self._current_weather_key)
                elif self._weather_forecast_key in air_command and \
                        air_command.replace(self._weather_forecast_key, '') == ' ':
                    self._send_chat_weather(self._weather_forecast_key)
                else:
                    self._socket_network.send_message(
                        self._network_commons.get_chat_message_category(),
                        AirBotUtils.air_help_message()
                    )
        return True

    def _send_chat_weather(self, request_type: str):
        weather_summary: str = 'Sorry, unable to compute'
        if request_type == self._current_weather_key:
            weather_summary: str = AirBotUtils.current_weather_summary(
                self._air_db.get_current_weather(),
                self._timezone
            )
        elif request_type == self._weather_forecast_key:
            weather_summary: str = AirBotUtils.forecast_weather_summary(
                self._air_db.get_weather_forecast(),
                self._timezone
            )
        self._socket_network.send_message(
            self._network_commons.get_chat_message_category(),
            weather_summary
        )


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')
        TIMEZONE: str = os.getenv('TIMEZONE')

        print(f'\nAir bot:')
        air_bot = AirBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, SQL_LITE_DB, TIMEZONE)
        air_bot.run_bot()
    except TypeError as type_error:
        logger.error(f'Received TypeError: Check that the .env project file is configured correctly... {type_error}')
        exit()
