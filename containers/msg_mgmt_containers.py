from containers.bot_containers import MessageConfig, ButtonSettings
from aiogram import types


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
