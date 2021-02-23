# Air weather, pollution and pollen properties

from typing import NoReturn, List, Any
from bin.climate_cell_units import metric_units, imperial_units


class Air:
    def __init__(self, unit_standard: str = 'metric', weather_data: dict = None, date: str = 'n/a') -> NoReturn:
        if unit_standard == 'imperial':
            self.unit_standard: dict = imperial_units
        else:
            self.unit_standard: dict = metric_units

        self.weather: dict = {
            'date': date,
            'temperature': 'n/a',
            'temperatureApparent': 'n/a',
            'moonPhase': 'n/a',
            'humidity': 'n/a',
            'dewPoint': 'n/a',
            'weatherCode': 'n/a',
            'precipitationProbability': 'n/a',
            'precipitationType': 'n/a',
            'pressureSurfaceLevel': 'n/a',
            'epaIndex': 'n/a',
            'epaHealthConcern': 'n/a',
            'epaPrimaryPollutant': 'n/a',
            'particulateMatter10': 'n/a',
            'particulateMatter25': 'n/a',
            'pollutantCO': 'n/a',
            'pollutantNO2': 'n/a',
            'pollutantO3': 'n/a',
            'pollutantSO2': 'n/a',
            'grassIndex': 'n/a',
            'treeIndex': 'n/a',
            'weedIndex': 'n/a'
        }
        self.single_value_attributes: List[str] = ['moonPhase', 'weatherCode', 'precipitationType',
                                                   'epaHealthConcern', 'epaPrimaryPollutant',
                                                   'grassIndex', 'treeIndex', 'weedIndex', 'date']
        if weather_data:
            for key in weather_data:
                self.__set_weather_attribute(key, weather_data[key])

    def __set_weather_attribute(self, attribute_type: str, attribute_value: Any) -> NoReturn:
        if attribute_type in self.single_value_attributes:
            if isinstance(attribute_value, int):
                self.weather[f'{attribute_type}'] = self.unit_standard[f'{attribute_type}'][f'{attribute_value}']
            else:
                self.weather[f'{attribute_type}'] = attribute_value
        else:
            self.weather[f'{attribute_type}'] = {}
            self.weather[f'{attribute_type}']['value'] = attribute_value
            self.weather[f'{attribute_type}']['unit'] = self.unit_standard[f'{attribute_type}']

    def __air_to_string(self, output_type: str, data: dict) -> str:
        data_as_string = ''
        for key in data:
            if key in self.single_value_attributes:
                if output_type == 'summary':
                    data_as_string += f'{key}: {data[key]},'
                else:
                    data_as_string += f'{data[key]},'
            else:
                if output_type == 'summary':
                    data_as_string += f'{key}: {data[key]["value"]}{data[key]["unit"]},'
                else:
                    data_as_string += f'{data[key]["value"]},'
        return data_as_string.rstrip(',')

    def __str__(self) -> str:
        return f'{self.__air_to_string("summary", self.weather)}'

    def __get_sub_dict(self, key_array) -> dict:
        return {k: self.weather[k] for k in self.weather.keys() & key_array}

    def set_weather_with_array(self, data_array: List) -> NoReturn:
        weather_keys = list(self.weather.keys())
        for index in range(len(data_array)):
            if data_array[index] != 'n/a':
                self.__set_weather_attribute(weather_keys[index], data_array[index])

    def get_all_weather(self) -> dict:
        return self.weather

    def get_basic_weather(self) -> dict:
        return self.__get_sub_dict(['date', 'temperature', 'temperatureApparent', 'moonPhase', 'humidity', 'dewPoint',
                                    'weatherCode', 'precipitationProbability', 'precipitationType',
                                    'pressureSurfaceLevel'])

    def get_pollution(self) -> dict:
        return self.__get_sub_dict(['date', 'epaIndex', 'epaHealthConcern', 'epaPrimaryPollutant',
                                    'particulateMatter10', 'particulateMatter25', 'pollutantCO', 'pollutantNO2',
                                    'pollutantO3', 'pollutantSO2'])

    def get_pollen(self) -> dict:
        return self.__get_sub_dict(['date', 'grassIndex', 'treeIndex', 'weedIndex'])

    def get_date(self) -> str:
        return self.weather['date']

    def data_to_csv_string(self) -> str:
        data_string = f'{self.__air_to_string("csv", self.weather)}'
        return data_string

    def data_key_order(self) -> str:
        data_as_string = ''
        for index in self.weather:
            data_as_string += f'{index},'
        return data_as_string.rstrip(',')
