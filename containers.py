import re

from aiogram import types

from constants import errors, error_types


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


class GroupMessagesContainer:
    def __init__(self):
        self.__messages: list[types.message] = []
        self.__messages_config: list[MessageConfig] = []

        self.__menu_config = []

    def __len__(self):
        return len(self.__messages)

    def __bool__(self):
        return bool(self.__messages_config)

    @property
    def messages(self) -> list[types.message]:
        return self.__messages

    @property
    def is_full_sent(self) -> bool:
        if self.__messages:
            return bool(len(self.__messages_config) - len(self.__messages))
        return False

    @property
    def configs(self) -> list[MessageConfig]:
        if not self.is_full_sent:
            return self.__messages_config[len(self.__messages) - 1:]
        return []

    def start_session(self, messages_config: tuple[MessageConfig], menu_config: MessageConfig):
        self.__menu_config = menu_config
        self.__messages_config = messages_config

    def stop_session(self):
        self.__messages = []
        self.__messages_config = []

    def append(self, message: types.message):
        self.__messages.append(message)

    def search(self, search_data: str) -> list[MessageConfig]:
        pass


class PhotoContainer:
    def __init__(self):
        self._paths: tuple[str, ...] = ()

    def __bool__(self):
        return bool(len(self._paths))

    @property
    def paths(self):
        return self._paths

    def set_paths(self, paths: tuple[str, ...]):
        self._paths = paths

    def clear(self):
        self._paths = ()


class MenuGroupContainer:
    def __init__(self, matrix_size: int):
        self._settings: list[list[ButtonSettings], ...] = [[]]
        self._page_matrix: int = 0

        self._matrix_size = matrix_size

        self._back_path = ''
        self._reset_path = ''

        self._additional_keyboard: tuple[tuple[str, str], ...] | None = None

    def __bool__(self):
        return bool(len(self._settings[0]))

    def __str__(self):
        return f'Count pages: {len(self._settings)}, page: {self._page_matrix}'

    @property
    def back_path(self):
        return self._back_path

    @property
    def reset_path(self):
        return self._reset_path

    @property
    def page(self):
        return self._page_matrix

    @property
    def len_pages(self):
        return len(self._settings)

    @property
    def is_end_page(self):
        return len(self._settings) == self._page_matrix+1

    @property
    def settings(self) -> tuple[ButtonSettings, ...]:
        return tuple(self._settings[self._page_matrix])

    @property
    def size(self):
        return self._matrix_size

    @property
    def additional_keyboard(self) -> tuple[tuple[str, str], ...] | None:
        return self._additional_keyboard

    def button_setting(self, number: int):
        return self._settings[self._page_matrix][number]

    def append(self, button_settings: ButtonSettings):
        if len(self._settings[-1]) == self._matrix_size:
            self._settings.append([])
        self._settings[-1].append(button_settings)

    def add_back_path(self, path: str):
        self._back_path = path

    def add_reset_path(self, path: str):
        self._reset_path = path

    def add_additional_keyboard(self, keyboard: tuple[tuple[str, str], ...]):
        self._additional_keyboard = keyboard

    def next_page(self):
        self._page_matrix += 1

    def back_page(self):
        self._page_matrix -= 1

    def search(self, data_search: str) -> tuple[ButtonSettings, ...]:
        buttons = []
        data_search = data_search.lower()

        for page in self._settings:
            for button in page:
                text = button.text.lower()
                if data_search in text:
                    buttons.append(button)

        return tuple(buttons)

    def clear(self):
        self._settings = [[]]
        self._page_matrix = 0


class ContainerData:
    def __init__(self, name: str, value: any = None):
        self._name = name
        self._value = value

    def __str__(self):
        return f'Name: {self._name}; Value: {self._value}'

    def new_value(self, value: any):
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name


class FillingContainerData(ContainerData):
    NEW_STATUS = ' ✅'

    def __init__(self, name: str, type_input: str, value: any = None, status: str = ' ❌'):
        super().__init__(name, value)

        self._status = status
        self._type_input = type_input

    def __str__(self):
        return f'Name: {self._name}; Status: {self._status}; Value: {self._value}'

    def new_value(self, value: any):
        self._value = value
        self.update_status()

    @property
    def status(self):
        return self._status

    @property
    def type_input(self):
        return self._type_input

    def update_status(self):
        self._status = self.NEW_STATUS


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


class BlackUserContainer:
    def __init__(self, id_user: int, date: str, name: str = '', tag: str = ''):
        self._name = name
        self._id = id_user
        self._date = date
        self._tag = tag

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @property
    def tag(self):
        return self._tag

    @property
    def initial_user(self) -> str:
        if self._name:
            return self._name
        return str(self._id)


class BotsConfigMessage:
    def __init__(self):
        self._bots_config_message: MessageConfig() = None

    def __bool__(self):
        return self._bots_config_message is not None

    def update_config(self, new_setting: MessageConfig):
        self._bots_config_message = new_setting

    @property
    def configs(self) -> MessageConfig:
        return self._bots_config_message
