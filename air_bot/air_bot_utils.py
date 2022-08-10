from datetime import datetime
import pytz
from air_core.library.climate_cell_units import weather_code_emojis
from air_core.library.types.types import Unit
from air_core.library.air import Air


class AirBotUtils:
    @staticmethod
    def spaces(number_of_spaces: int):
        spaces: str = ''
        for i in range(number_of_spaces):
            spaces = spaces + ' '
        return spaces

    @staticmethod
    def current_weather_summary(current_weather: dict, timezone: str) -> str:
        return f'{AirBotUtils.weather_summary("current", current_weather, timezone)}\n'

    @staticmethod
    def forecast_weather_summary(forecast_weather: list[dict], timezone: str) -> str:
        title_space: int = 0
        forecasts: str = ''.join(f'{AirBotUtils.weather_summary("forecast", forecast, timezone)}\n'
                                 for index, forecast in enumerate(forecast_weather) if index > 0)
        return f'{AirBotUtils.spaces(title_space)}{len(forecast_weather) - 1} Day Forecast\n{forecasts}'

    @staticmethod
    def time_format_morph(time_stamp: str) -> str:
        time_morph: str = '-'.join(time_stamp.split('-')[:-1])
        if '.' in time_morph:
            time_morph: str = time_morph.split('.')[:-1][0]
        return time_morph

    @staticmethod
    def weather_summary(summary_type: str, weather_data: dict, timezone: str) -> str:
        weather_space: int = 11
        weather_units: dict = Air(Unit.imperial).get_units(Unit.imperial)
        if 'Z' in weather_data['date']:
            weather_time_format: str = '%Y-%m-%dT%H:%M:%SZ'
            weather_time: str = weather_data['date']
            raw_time = datetime.strptime(weather_time, weather_time_format)
            date_time: datetime = datetime(
                int(raw_time.strftime('%Y')), int(raw_time.strftime('%m')),
                int(raw_time.strftime('%d')), int(raw_time.strftime('%H')),
                int(raw_time.strftime('%M')), int(raw_time.strftime('%S')),
                0, tzinfo=pytz.utc
            )
            date_time = date_time.astimezone(pytz.timezone(timezone))
        else:
            weather_time_format: str = '%Y-%m-%dT%H:%M:%S'
            weather_time: str = AirBotUtils.time_format_morph(weather_data['date'])
            date_time: datetime = datetime.strptime(weather_time, weather_time_format)
        time = ''
        moon_data: str = ''
        pollen_index: int = max([weather_data['grassIndex'], weather_data['treeIndex'], weather_data['weedIndex']])
        precipitation_report: str = \
            f'{weather_data["precipitationProbability"]} {weather_units["precipitationProbability"]} chance of ' \
            f'{"Rain" if weather_data["precipitationType"] == "N/A" else weather_data["precipitationType"]}'

        if summary_type == 'current':
            time = date_time.strftime('%H:%M')
        elif summary_type == 'forecast':
            time = date_time.strftime('%m/%d')
            moon_data = f', with a {weather_data["moonPhase"]} Moon'

        try:
            return f'{AirBotUtils.weather_emoji(weather_data["weatherCode"])}️  {time} | ' \
                   f'{weather_data["weatherCode"]}, ' \
                   f'feels like {weather_data["temperatureApparent"]} {weather_units["temperatureApparent"]}' \
                   f'{moon_data}\n' \
                   f'{AirBotUtils.spaces(weather_space)} {precipitation_report} with ' \
                   f'{weather_data["humidity"]} {weather_units["humidity"]} Humidity\n' \
                   f'{AirBotUtils.spaces(weather_space)} {weather_data["pressureSurfaceLevel"]} ' \
                   f'{weather_units["pressureSurfaceLevel"]} Pressure ' \
                   f'with {weather_data["epaHealthConcern"]} Air Quality ' \
                   f'and Pollen level {pollen_index} severity'
        except TypeError as type_error:
            print(f'Received error (chat_message_builder): {str(type_error)}')

    @staticmethod
    def weather_emoji(emoji_key: str) -> str:
        return weather_code_emojis[f'{emoji_key}']

    @staticmethod
    def air_help_message() -> str:
        help_spaces: int = 5
        return f'  🤔 \n\n*/air* weather commands are as follows:\n\n' \
               f'{AirBotUtils.spaces(help_spaces)}`/air current` : gives the most current weather data\n' \
               f'{AirBotUtils.spaces(help_spaces)}`/air forecast` : gives 4 day weather forecast, including today\'s\n'
