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
