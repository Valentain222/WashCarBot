from containers import MessageConfig, ButtonSettings, CallBackData
create_callback = CallBackData.creating_callback

from . import texts, buttons, constants, functions


BLACK_USER = MessageConfig(text_message='Извините, вы в черном списке')

SUCCESSFUL_SAVE_MESSAGE = MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU,
                                                                        buttons.BACK_TEXT),),
                                        row_buttons=1,
                                        text_message=texts.SUCCESSFUL_SAVING_TEXT,
                                        parse_mode=constants.PARSE_MODE1)
SUCCESSFUL_SEND_MESSAGE = MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU,
                                                                        'Заполнить еще 🔄'),
                                                         buttons.BACK_MAIN_MENU),
                                        row_buttons=1,
                                        text_message='Данные успешно занесены в таблицу ✅')

INPUT_NEW_PASSWORD = MessageConfig(button_settings=buttons.INPUT_PASSWORD_BACK,
                                   text_message='Введите новый пароль: ',
                                   row_buttons=1)
SUCCESSFUL_DELETE_USER = MessageConfig(button_settings=(ButtonSettings(create_callback('interaction', 'black_list',
                                                                                       'start'),
                                                                       buttons.BACK_TEXT),),
                                       text_message='Пользователь разблокирован',
                                       row_buttons=1)
SEARCH_INPUT_PROMPTS = MessageConfig(text_message='Введите текстовый запрос для поиска')

ADMIN_MENU = MessageConfig(
            button_settings=(
                ButtonSettings('interaction.black_list/start', 'Черный список 🚫'),
                ButtonSettings('interaction.passwords/start', 'Пароли 🔒'),
                ButtonSettings('interaction.parameters/start', 'Параметры заполнения таблицы 📜'),
                buttons.BACK_MAIN_MENU
            ),
            row_buttons=1,
            text_message='Отредактировать...'
            )

MAIN_MENU = MessageConfig(
        button_settings=(
            ButtonSettings(create_callback(constants.BASIC_GROUP, constants.USER_STATE_NAME_ANALYST),
                           'Аналитик 📊'),
            ButtonSettings(create_callback(constants.BASIC_GROUP, constants.USER_STATE_NAME_OPERATOR),
                           'Оператор учета 🗂'),
            ButtonSettings(create_callback(constants.BASIC_GROUP, constants.USER_STATE_NAME_ADMIN),
                           'Администратор 🔑')
        ),
        row_buttons=2,
        text_message=(
            'От чьей должности вы желаете продолжить?'
            '\n\n*Аналитик* \\- Просмотр статистики и ее настройка '
            '\n*Оператор учета* \\- Внесение отчета в единый реестр'
            '\n*Администратор* \\- Настройки бота'
        ),
        parse_mode=constants.PARSE_MODE1
    )

DATA_START_SUCCESS_MENU = MessageConfig(button_settings=(ButtonSettings(constants.MAIN_MENU, 'К работе 🚀'),),
                                        row_buttons=1, text_message='Привет! С началом рабочего дня!')

DATA_LOG_IN_MESSAGE = MessageConfig(button_settings=(ButtonSettings(constants.MAIN_MENU, buttons.BACK_TEXT),),
                                    row_buttons=2, text_message='_Введите пароль\\: _',
                                    parse_mode=constants.PARSE_MODE1)

DATA_TRUTH_PASSWORD_MESSAGE = MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU, 'Далее ➡'),),
                                            row_buttons=1, text_message='_Введён правильный пароль ✅_',
                                            parse_mode=constants.PARSE_MODE1)
UNEXPECTED_MESSAGE_RECEIVED_AFTER_START = MessageConfig(button_settings=buttons.BACK_BUTTON_SETTINGS, row_buttons=1,
                                                        text_message='Сейчас говорю Я!!!! Используйте кнокпи')
UNEXPECTED_MESSAGE_RECEIVED_BEFORE_START = MessageConfig(text_message='Тапните на /start')
WRONG_INPUT_DATE_MESSAGE = MessageConfig(text_message='Вы неправильно ввели дату!!')
WRONG_INPUT_PROMPTS_MESSAGE = MessageConfig(button_settings=buttons.BACK_BUTTON_SETTINGS,
                                            row_buttons=1,
                                            text_message='Вы использовали запрещенные символы!')
DATA_OPERATOR_INPUT_PROMPTS = MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU,
                                                                            buttons.BACK_TEXT),),
                                            row_buttons=1,
                                            text_message=('Введите целое число\\:\n'
                                                          ' _Прибыль указывается в рублях, а скидка в процентах_'),
                                            parse_mode=constants.PARSE_MODE1)
DATA_OPERATOR_FILLED_FAILURE = MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU,
                                                                             buttons.BACK_TEXT),),
                                             text_message='Вы заполнили не все данные!',
                                             row_buttons=1)
ANALYST_MAIN_MENU = MessageConfig(button_settings=(ButtonSettings('interaction.open', 'Статистика 📊'),
                                                   ButtonSettings('interaction.edit/start', 'Настройки ⚙'),
                                                   buttons.BACK_MAIN_MENU),
                                  row_buttons=2,
                                  text_message='Выберите')
SAVE_PASSWORD = MessageConfig(button_settings=buttons.INPUT_PASSWORD_BACK,
                              text_message='Пароль сохранен',
                              row_buttons=1)
CAPACITY_SLIDER = MessageConfig(
                                button_settings=functions.make_slider('capacity', range(1, 4, 1)),
                                row_buttons=2,
                                text_message='Выберите вместимость:'
                            )
RATING_SLIDER = MessageConfig(
    button_settings=functions.make_slider('rating', range(1, 11, 1)),
    row_buttons=5,
    text_message='Выберите оценку:'
)

LOADING_MESSAGE = MessageConfig(text_message='Загружаю ⏳')
