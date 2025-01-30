from constants import error_types, errors
from aiogram import types


class CallBackData:
    def __init__(self):
        self._group: str = ''
        self._state: str = ''
        self._event: str = ''
        self._parallel_action: str = ''

    def __str__(self):
        return f'{self._group}.{self._state}/{self._event}|{self._parallel_action}'

    @property
    def group(self) -> str:
        return self._group

    @property
    def state(self) -> str:
        return self._state

    @property
    def event(self) -> str:
        return self._event

    @property
    def parallel_action(self) -> str:
        return self._parallel_action

    @staticmethod
    def __is_truth_callback_data(data: list, callback_data: str):
        if len(data) != 2:
            raise error_types.WrongCallbackType(callback_data)

    @staticmethod
    def __split_callback(seps: tuple[str, ...], callback_data: str) -> None | str:
        for sep in seps:
            if sep in callback_data:
                return sep

    def callback_division(self, callback_data: str) -> None:
        if not callback_data:
            raise ValueError('Callback is clean!')
        if not isinstance(callback_data, str):
            raise error_types.WrongType(str(type(callback_data)))

        sep = self.__split_callback(('.', '||'), callback_data)
        if sep:
            data = callback_data.split(sep)
            self.__is_truth_callback_data(data, callback_data)
            self._group, other_group = data
        else:
            self._group = callback_data
            other_group = ''

        if other_group:
            if '||' in other_group:
                data = other_group.split('||')
                self.__is_truth_callback_data(data, callback_data)
                state_group, self._parallel_action = data
            else:
                state_group = other_group

            if state_group:
                if '/' in state_group:
                    self._state, self._event = state_group.split('/')
                else:
                    self._state = state_group

    @staticmethod
    def creating_callback(group: str, state: str = '', event: str = '', parallel_action: str = '') -> str:
        callback = group + (f'.{state}' if state else '') + \
                   (f'/{event}' if event and state else '') + \
                   (f'||{parallel_action}' if parallel_action else '')

        return callback


class ButtonSettings:
    def __init__(self, callback: str, text: str):
        self._text = text
        self._callback = callback

    @property
    def text(self) -> str:
        return self._text

    @property
    def callback(self) -> str:
        return self._callback

    @property
    def button_settings(self) -> tuple[str, str]:
        return self._callback, self._text

    def __str__(self):
        return f'Text: {self._text}, callback: {self._callback}'

    def __eq__(self, other):
        if isinstance(other, ButtonSettings):
            return other.text == self._text and other.callback == self._callback
        return False

    def __bool__(self):
        return bool(self._text) and bool(self._callback)


class MessageConfig:
    def __init__(self, button_settings: tuple[tuple[ButtonSettings, ...], ...] | tuple[ButtonSettings, ...] = (),
                 row_buttons: int | tuple = 1, text_message: str = '', parse_mode: str | None = None):
        if button_settings:
            if (count := self.count_tuples(button_settings[0])) < 1:
                button_settings = (button_settings,)

        if isinstance(row_buttons, int):
            row_buttons = (row_buttons,)

        self.__button_settings = button_settings
        self.__row = row_buttons
        self.__text = text_message
        self.__parse_mode = parse_mode

    @property
    def button_settings(self):
        return self.__button_settings

    @property
    def row(self):
        return self.__row

    @property
    def text(self):
        return self.__text

    @property
    def parse_mode(self):
        return self.__parse_mode

    def count_tuples(self, nested_tuple):
        count = 0
        if not isinstance(nested_tuple, ButtonSettings):
            count += 1
            for item in nested_tuple:
                if isinstance(item, tuple):
                    count += 1
                    count += self.count_tuples(item[0])
        return count

    def __str__(self):
        return f'text: {self.__text}, button_settings: {self.__button_settings}, ' \
               f'row: {self.__row}, parse_mode: {self.__parse_mode}'


class StateUserContainer:
    def __init__(self):
        self._state = ''
        self._user = ''

    def __bool__(self):
        return bool(len(self._state)) or bool(len(self._user))

    def __str__(self):
        return f'State: {self._state}, user: {self._user}'

    @property
    def state(self):
        return self._state

    @property
    def user(self):
        return self._user

    def update_state(self, new_state: str):
        if not isinstance(new_state, str):
            raise errors.WRONG_TYPE
        self._state = new_state

    def update_user(self, new_user: str):
        if not isinstance(new_user, str):
            raise errors.WRONG_TYPE
        self._user = new_user

    def clear(self):
        self._state = ''
        self._user = ''
