class InvalidError(Exception):
    def __init__(self, type: str, event: str, available_events=()):
        self._type = type
        self._event = event
        self._available_events = available_events

    def __str__(self):
        available = ''
        if self._available_events:
            available = f"Available: {'; '.join(self._available_events)}"
        return f'Wrong {self._type}: {self._event}. {available}'


class EventSintaxisError(Exception):
    def __init__(self, event: str):
        self._event = event

    def __str__(self):
        return f'The event "{self._event}" is incorrectly composed'


class CleanData(Exception):
    def __init__(self, type_data: str, state: str = 'clear'):
        self._type_data = type_data
        self._state = state

    def __str__(self):
        return f'{self._type_data} is {self._state}!'


class WrongEvent(Exception):
    def __init__(self, event: str):
        self._event = event

    def __str__(self):
        return f'Wrong event: {self._event}'


class WrongType(Exception):
    def __init__(self, type_obj: str):
        self._type = type_obj

    def __str__(self):
        return f'Wrong type {self._type}!'


class WrongCallbackType(Exception):
    def __init__(self, callback: str):
        self._callback = callback

    def __str__(self):
        return f'Wrong Callback: {self._callback}! Truth group.state/event||parallel_action'

