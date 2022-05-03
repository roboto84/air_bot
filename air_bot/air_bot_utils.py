from datetime import datetime
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
    def current_weather_summary(current_weather: dict) -> str:
        return f'{AirBotUtils.weather_summary("current", current_weather)}\n'

    @staticmethod
    def forecast_weather_summary(forecast_weather: list[dict]) -> str:
        title_space: int = 5
        forecasts: str = ''.join(f'{AirBotUtils.weather_summary("forecast", forecast)}\n'
                                 for index, forecast in enumerate(forecast_weather) if index > 0)
        return f'\n{AirBotUtils.spaces(title_space)}{len(forecast_weather)-1} Day Forecast\n{forecasts}'

    @staticmethod
    def time_format_morph(time_stamp: str) -> str:
        time_morph: str = '-'.join(time_stamp.split('-')[:-1])
        if '.' in time_morph:
            time_morph: str = time_morph.split('.')[:-1][0]
        return time_morph

    @staticmethod
    def weather_summary(summary_type: str, weather_data: dict) -> str:
        weather_space: int = 11
        weather_units: dict = Air(Unit.imperial).get_units(Unit.imperial)
        date_time = datetime.strptime(AirBotUtils.time_format_morph(weather_data['date']), '%Y-%m-%dT%H:%M:%S')
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
            return f'\n{AirBotUtils.weather_emoji(weather_data["weatherCode"])}️  {time} | ' \
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
        return f'  🤔 \n\n"/air" weather commands are as follows:\n\n' \
               f'{AirBotUtils.spaces(help_spaces)}/air current : gives the most current weather data\n' \
               f'{AirBotUtils.spaces(help_spaces)}/air forecast : gives 4 day weather forecast, including today\'s\n'
