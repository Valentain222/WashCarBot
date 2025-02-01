import sqlite3
from containers.data_containers import ContainerData, BlackUserContainer


class SQliteTools:

    def __init__(self):

        self.cursor = None
        self.connect = None

        self.connection()

    def connection(self):
        connection = sqlite3.connect("Data_Base.db")
        cursor = connection.cursor()

        self.cursor = cursor
        self.connect = connection

    def read(self, table_name, column):

        conditions = " AND".join([f"{col} IS NOT NULL" for col in column.split(',')])
        request_code = f"SELECT {column} FROM {table_name}"
        if column != '*':
            request_code += f"\nWHERE {conditions}"

        self.cursor.execute(request_code)

        return self.cursor.fetchall()

    def add_to_table(self, table_name, column, new_data):

        request_code = f"""INSERT INTO {table_name}({column})
                            VALUES {new_data}"""

        self.cursor.execute(request_code)
        self.connect.commit()

    def delete_from_table(self, table_name, string_id, column, meaning):

        columns = ','.join([f'{col} = {meaning}' for col in column.split(',')])
        request_code = f"""UPDATE {table_name}
                           SET {columns}
                           WHERE id = {string_id}"""

        self.cursor.execute(request_code)
        self.connect.commit()

    def reset(self, delete, table_name, values, column):
        request_code = f'DELETE FROM {table_name}'
        self.cursor.execute(request_code)
        self.connect.commit()
        if not delete:
            self.add_to_table(table_name, column, values)

    def fetch_password(self, post: str) -> str:
        self.read("passwords", "post, password")
        return '13119'

    def is_in_black_list(self, user_id: str) -> bool:
        return True

    def add_to_black_list(self, user_id, nick_name):
        pass

    def save_data(self, data: dict):
        pass

    def passwords(self) -> dict:
        return {
            'data_operator': ContainerData(name='Дата оператор', value='123'),
            'analyst': ContainerData(name='Аналитик', value='456'),
            'admin': ContainerData(name='Админ', value='789')
        }

    def save_password(self, name_user: str, new_password: str):
        pass

    def black_users(self) -> tuple[BlackUserContainer, ...]:
        return (BlackUserContainer(name='Николай', id_user=123456, date='2022.05.09', tag='@f'),
                BlackUserContainer(name='Алексей', id_user=234567, date='2022.06.15', tag='@rte'),
                BlackUserContainer(name='Мария', id_user=345678, date='2022.07.20'),
                BlackUserContainer(id_user=456789, date='2022.08.25'),
                BlackUserContainer(name='Дмитрий', id_user=567890, date='2022.09.30'))

    def delete_user(self, id_user: int):
        pass

    def parameters(self):
        return {
            'services': ContainerData(name='Услуги', value=('Мойка',
                    'Чистка',
                    'Мойка салона',
                    'Мойка кузова',
                    'Мойка бампера',
                    'Чистка двигателя',
                    'Полировка кузова',
                    'Нанесение воска',
                    'Чистка колес',
                    'Чистка стекол',
                    'Удаление вмятин',
                    'Антигравийная обработка',
                    'Обработка кожи',
                    'Удаление запахов',
                    'Мойка подкапотного пространства',
                    'Чистка кондиционера',
                    'Обработка пластиковых элементов',
                    'Нанесение защитного покрытия',
                    'Шампунь для кузова',
                    'Чистка ковров и обивки',
                    'Обработка антикоррозийными средствами',
                    'Мойка двигателя паром',
                    'Сушка кузова',
                    'Проверка и долив жидкостей',
                    'Замена фильтров')),
            'car_washes': ContainerData(name='Автомойка', value=("Чистая машина",
                "Блестящий авто",
                "АвтоСияние",
                "Мойка на улице",
                "СуперЧистота",
                "АвтоГладь",
                "Блеск и Shine",
                "Гармония авто",
                "Эксперт Мойки",
                "Светлый путь")),

            'stamps': ContainerData('Марки', value=(
                                                    "Toyota",
                                                    "Ford",
                                                    "Honda",
                                                    "Chevrolet",
                                                    "Nissan",
                                                    "Volkswagen",
                                                    "BMW",
                                                    "Mercedes-Benz",
                                                    "Audi",
                                                    "Hyundai",
                                                    "Kia",
                                                    "Subaru",
                                                    "Mazda",
                                                    "Porsche",
                                                    "Lexus",
                                                    "Jaguar",
                                                    "Land Rover",
                                                    "Fiat",
                                                    "Tesla",
                                                    "Volvo"))
        }

    def add_parameter(self, parameter: str):
        pass

    def delete_parameter(self, parameter_key: str):
        pass

sql_connect = SQliteTools()
