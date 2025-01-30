from containers.data_containers import ContainerData, BlackUserContainer, FillingContainerData

from constants import error_types, errors


# Base Managers

class DataManager:
    def __init__(self, data: dict):
        self._data = data

    def __bool__(self):
        return len(self._data)

    @property
    def data(self) -> dict:
        return self._data

    def truth_container_name(self, key: str) -> None:
        if key not in self._data.keys():
            raise error_types.InvalidError('key', key, self._data.keys())

    def get_data(self, key: str) -> dict:
        self.truth_container_name(key)

        return self._data.get(key)

    def get_key(self, index: int) -> str:
        if index > len(self._data.keys())-1:
            raise errors.OUT_INDEX

        return list(self._data.keys())[index]

    def update_data(self, new_data: any) -> None:
        self._data = new_data

    def reset(self):
        pass


# Modes for DataManager

class Mode:
    def __init__(self, data_manager: DataManager):
        self._data_manager = data_manager


class StorageDataManager(Mode):
    def __init__(self, data_manager: DataManager):
        super().__init__(data_manager)

        self._remember_key: str = ''
        self._remember_data = None

    @property
    def remember_key(self) -> str:
        return self._remember_key

    @property
    def remember_data(self) -> any:
        return self._remember_data

    def remembered_data(self, key: str) -> dict:
        if self._data_manager.data:
            self._data_manager.truth_container_name(key)
            self._remember_data, self._remember_key = self._data_manager.data.get(key), key

            return self._data_manager.data

        return {}


class ContainerDataManager(Mode):
    def __init__(self, manager: DataManager):
        super().__init__(manager)

    @property
    def is_filled(self) -> bool:
        for container in self._data_manager.data.values():
            value = container.value
            if not value:
                return False
        return True

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(value.name for value in self._data_manager.data.values())

    def add_value(self, name_container: str, value: any):
        self._data_manager.truth_container_name(name_container)
        self._data_manager.data[name_container].new_value(value)

    def value(self, name_container: str) -> any:
        self._data_manager.truth_container_name(name_container)

        return self._data_manager.data.get(name_container).value


# Manual managers

class FillingManager(DataManager, ContainerDataManager):
    def __init__(self, filling_parameters: dict[str: FillingContainerData, ...]):
        DataManager.__init__(self, filling_parameters)

        ContainerDataManager.__init__(self, self)

    def __str__(self):
        state = (f'{key}: {value}' for key, value in self._data.items())
        return '\n'.join(state)

    def type_input(self, name_container: str) -> str:
        self._data_manager.truth_container_name(name_container)

        return self._data.get(name_container).type_input


class SettingsManager(DataManager, StorageDataManager, ContainerDataManager):
    def __init__(self, data: dict[str: ContainerData] = None):
        if data is None:
            data = {}
        DataManager.__init__(self, data)

        ContainerDataManager.__init__(self, self)
        StorageDataManager.__init__(self, self)


class BlackListManager:
    def __init__(self):
        self._users: tuple[BlackUserContainer, ...] = ()
        self._user = None

    def update_users(self, users: tuple[BlackUserContainer, ...]):
        self._users = users

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(user.initial_user for user in self._users)

    def remember_user(self, index):
        if index > len(self._users)-1:
            raise error_types.InvalidError('index', index, f'index > {len(self._users)-1}')
        self._user = self._users[index]

        return self._user

    @property
    def string_data_remember_user(self) -> str:
        return f'Имя: {self._user.name},\n' if self._user.namee else '' + (f'Тэг: {self._user.tag},\n'
                                                                           if self._user.tag else '') \
                                                                     + (f'ID: {self._user.id},'
                                                                        f'\nДата блокировки: {self._user.date}')

    @property
    def remembered_user(self) -> BlackUserContainer:
        return self._user
