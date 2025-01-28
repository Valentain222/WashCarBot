import json
from constants import error_types


class JsonDataHandler:
    def __init__(self, file):

        self._file_name = file
        self._data = None

        self._get_data()

    def _get_data(self):
        with open(self._file_name, 'r', encoding='utf-8') as json_file:
            self._data = json.load(json_file)

    def _convert_to_serializable(self, value):
        if isinstance(value, tuple):
            return list(value)
        elif isinstance(value, dict):
            return {k: self._convert_to_serializable(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_to_serializable(v) for v in value]
        elif isinstance(value, object) and value.__class__.__module__ != 'builtins':
            raise error_types.WrongType(str(type(value)))

        return value

    def update_data(self, name: str, value: any):
        value = self._convert_to_serializable(value)
        self._data[name] = value

        with open(self._file_name, 'w') as json_file:
            json.dump(self._data, json_file)


class JsonDictsHandler(JsonDataHandler):
    def __init__(self, file: str):
        super().__init__(file)

    def __validate_key(self, key):
        if key not in self._data:
            raise error_types.InvalidError('key', key, tuple(self._data.keys()))

    def get_value(self, name: str):
        self._get_data()
        self.__validate_key(name)

        return self._data.get(name)

    def update_dict(self, name: str, value: any):
        self.__validate_key(name)

        self.update_data(name, value)
