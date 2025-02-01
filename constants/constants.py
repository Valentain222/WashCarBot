import re
from containers.data_containers import FillingContainerData
from containers.bot_containers import CallBackData

create_callback = CallBackData.creating_callback

DATE_PATTERN = re.compile(r'^\d{4}\.(0[1-9]|1[0-2])\.(0[1-9]|[12][0-9]|3[01])$')

PARSE_MODE1 = 'MarkdownV2'

BASIC_GROUP = 'basic'

USER_STATE_NAME_OPERATOR = 'data_operator'
USER_STATE_NAME_ADMIN = 'admin'
USER_STATE_NAME_ANALYST = 'analyst'

MAIN_MENU = create_callback('basic', 'main_menu')
INTERACTION_MAIN_MENU = create_callback('interaction', 'main')

LEN_GROUP_MESSAGES = 4
LEN_MENU = 4

MENU_BUTTONS_ROW = 1
MENU_ROW = 2

FILLING_OPERATOR_MENU = {'services': FillingContainerData(name='Услуги', type_input='menu'),
                         'rating': FillingContainerData(name='Оценка', type_input='slider'),
                         'date': FillingContainerData(name='Дата', type_input='date'),
                         'discount': FillingContainerData(name='Скидка', type_input='int'),
                         'stamp': FillingContainerData(name='Марка', type_input='menu'),
                         'profit': FillingContainerData(name='Прибыль', type_input='int'),
                         'car_wash': FillingContainerData(name='Автомойка', type_input='menu')}

FILLING_ANALYST_MENU = {'capacity': FillingContainerData(name='Вместимость 🧾', type_input='slider'),
                        'car_wash': FillingContainerData(name='Автомойка 🚘', type_input='menu'),
                        'date_start': FillingContainerData(name='Стартовая дата 🗓', type_input='date'),
                        'date_end': FillingContainerData(name='Конечная дата 📅', type_input='date')}
