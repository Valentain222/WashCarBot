from . import texts, constants

from containers import ButtonSettings

DATE_MANUAL_INPUT_TEXT = 'Ручной ввод ✍'
DATE_AUTO_INPUT_TEXT = 'Автоматическая 🔧'
BACK_TEXT = 'Обратно ↩'
OK = 'Ок'
DELETE_FROM_BLACK_LIST_TEXT = 'Удалить'
RESET_TEXT_GROUP_MENU = 'Обновить 🔄'
BACK_TEXT_GROUP_MENU = 'Выход 🚪'
SEND = 'Отправить ➡'
FORWARD = 'Далее ➡'
SEARCH_TEXT = 'Поиск 🔎'

FORWARD_TEXT = 'Вперед ⏩'
BACK_MENU_TEXT = '⏪ Назад'

INPUT_PASSWORD_BACK = (ButtonSettings('interaction.passwords/start', BACK_TEXT),)
PLOTS_MENU_BUTTON = (ButtonSettings('interaction.main||group_exit', BACK_TEXT),)
BACK_BUTTON_SETTINGS = (ButtonSettings('basic.back', BACK_TEXT),)
BACK_MAIN_MENU = ButtonSettings(constants.MAIN_MENU, 'Главное меню 🏠')

SUCCESSFUL_SAVING_TEXT = 'В меню'

MESSAGES_GROUP_MENU_BUTTONS = (ButtonSettings('menu_operation.show_more', 'Показать еще'),
                               ButtonSettings('menu_operation.search', SEARCH_TEXT))

MENU_BUTTONS = (ButtonSettings('menu_operation.search/start', SEARCH_TEXT),)
BACK_BUTTON = (ButtonSettings('menu_operation.browsing/back', BACK_MENU_TEXT),)
NEXT_BUTTON = (ButtonSettings('menu_operation.browsing/next', FORWARD_TEXT),)

RESET_BLACK_LIST = ButtonSettings('interaction.black_list/reset_table', 'Сбросить таблицу')
RESET_PASSWORDS = ButtonSettings('interaction.passwords/reset_passwords', 'Сбросить')

PARAMETERS_ADDITIONAL_KEYBOARD = (ButtonSettings('interaction.parameters/add', 'Добавить ➕'),
                                  ButtonSettings('interaction.parameters/reset_par', 'Сбросить'))
