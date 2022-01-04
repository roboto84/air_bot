# Air chat bot
import os
import logging.config
from sqlite3 import Row
from typing import Any, NoReturn, List
from dotenv import load_dotenv
from wh00t_core.library.client_network import ClientNetwork
from air_core.library.air_db import AirDb


class AirBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, sql_lite_db_path: str):
        self._logger: Any = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key_CURRENT = '/air'
        self._chat_key_FORECAST = '/forecast'
        self._air_db: AirDb = AirDb(logging_object, sql_lite_db_path)
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port, 'air_bot', 'app', logging)

    @staticmethod
    def _spaces(number_of_spaces: int):
        spaces: str = ''
        for i in range(number_of_spaces):
            spaces = spaces + ' '
        return spaces

    @staticmethod
    def _table_row_to_dict(row: Row) -> dict:
        data: dict = dict(row)
        return {
            'date': data['date'],
            'temperature': f"{data['temp_value']} {data['temp_unit']}",
            'temperatureApparent': f"{data['temp_apparent_value']} {data['temp_apparent_unit']}",
            'moonPhase': data['moon_phase'],
            'humidity': f"{data['humidity_value']} {data['humidity_unit']}",
            'dewPoint': f"{data['dew_point_value']} {data['dew_point_unit']}",
            'weatherCode': data['weather_code'],
            'precipitationProbability': f"{data['precipitation_probability_value']} "
                                        f"{data['precipitation_probability_unit']}",
            'precipitationType': data['precipitation_type'],
            'pressureSurfaceLevel': f"{data['pressure_surface_level_value']} {data['pressure_surface_level_unit']}",
            'epaIndex': f"{data['epa_index_value']} {data['epa_index_unit']}",
            'epaHealthConcern': data['epa_health_concern'],
            'epaPrimaryPollutant': data['epa_primary_pollutant'],
            'particulateMatter10': f"{data['particulate_matter10_value']} {data['particulate_matter10_unit']}",
            'particulateMatter25': f"{data['particulate_matter25_value']} {data['particulate_matter25_unit']}",
            'pollutantCO': f"{data['pollutant_CO_value']} {data['temp_apparent_unit']}",
            'pollutantNO2': f"{data['pollutant_NO2_value']} {data['pollutant_NO2_unit']}",
            'pollutantO3': f"{data['pollutant_O3_value']} {data['pollutant_O3_unit']}",
            'pollutantSO2': f"{data['pollutant_SO2_value']} {data['pollutant_SO2_unit']}",
            'grassIndex': data['grass_index'],
            'treeIndex': data['tree_index'],
            'weedIndex': data['weed_index']
        }

    def run_bot(self) -> NoReturn:
        try:
            self._socket_network.sock_it()
            self._socket_network.receive(self._receive_message_callback)
        except KeyboardInterrupt:
            self._logger.info('Received a KeyboardInterrupt... closing bot')
            exit()

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'air_bot']) and ('message' in package):
            if 'category' in package and package['category'] == 'chat_message' and \
                    isinstance(package['message'], str) and self._chat_key_CURRENT in package['message']:
                self._send_chat_weather(self._chat_key_CURRENT)
            elif 'category' in package and package['category'] == 'chat_message' and \
                    isinstance(package['message'], str) and self._chat_key_FORECAST in package['message']:
                self._send_chat_weather(self._chat_key_FORECAST)
        return True

    def _send_chat_weather(self, request_type: str):
        weather_summary: str = 'Sorry, unable to compute'
        if request_type == self._chat_key_CURRENT:
            self._socket_network.send_message('chat_message', f'Ok, getting current weather 🤔')
            weather_summary: str = self._current_weather_summary(self._get_current_data())
        elif request_type == self._chat_key_FORECAST:
            self._socket_network.send_message('chat_message', f'Ok, getting weather forecast 🤔')
            weather_summary: str = self._forecast_weather_summary(self._get_forecast_data())
        self._socket_network.send_message('chat_message', weather_summary)

    def _get_current_data(self) -> dict:
        current_weather: list[Row] = self._air_db.get_current_weather()
        return self._table_row_to_dict(current_weather[0])

    def _get_forecast_data(self) -> list[dict]:
        weather_forecast: list[Row] = self._air_db.get_forecast_weather()
        weather_forecast_dicts: list[dict] = [self._table_row_to_dict(row) for row in weather_forecast]
        return weather_forecast_dicts

    def _current_weather_summary(self, current_weather: dict) -> str:
        weather_space: int = 11
        current_weather: dict = current_weather
        try:
            return f'\n🌩️  Today: {current_weather["date"]}\n' \
                   f'{self._spaces(weather_space)} summary: {current_weather["weatherCode"]}\n' \
                   f'{self._spaces(weather_space)} moon: {current_weather["moonPhase"]}\n' \
                   f'{self._spaces(weather_space)} temp: {current_weather["temperature"]}' \
                   f'{self._spaces(weather_space)} temp apparent: {current_weather["temperatureApparent"]}\n' \
                   f'{self._spaces(weather_space)} humidity: {current_weather["humidity"]}' \
                   f'{self._spaces(weather_space)} dewPoint: {current_weather["dewPoint"]}\n' \
                   f'{self._spaces(weather_space)} rain prob.: {current_weather["precipitationProbability"]}' \
                   f'{self._spaces(weather_space)} rain type: {current_weather["precipitationType"]}\n' \
                   f'{self._spaces(weather_space)} pressure: {current_weather["pressureSurfaceLevel"]}\n' \
                   f'{self._spaces(weather_space)} epa index: {current_weather["epaIndex"]}' \
                   f'{self._spaces(weather_space)} epa health concern: {current_weather["epaHealthConcern"]}\n' \
                   f'{self._spaces(weather_space)} grass index: {current_weather["grassIndex"]}' \
                   f'{self._spaces(weather_space)} tree index: {current_weather["treeIndex"]}' \
                   f'{self._spaces(weather_space)} weed index: {current_weather["weedIndex"]}'
        except TypeError as type_error:
            print(f'Received error (chat_message_builder): {str(type_error)}')

    @staticmethod
    def _forecast_weather_summary(forecast_weather: List[dict]) -> str:
        return '... coming soon'


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')

        print(f'\nAir bot:')
        air_bot = AirBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, SQL_LITE_DB)
        air_bot.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
