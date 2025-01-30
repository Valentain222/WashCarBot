from bot_tools import MenuManager
from sq_functions import SQliteTools
from data_management import FillingContainer, SettingsManager, BlackListManager

from json_storage import JsonDictsHandler

from abc import abstractmethod, ABC

from containers.bot_containers import MessageConfig, StateUserContainer, ButtonSettings

from constants import texts, buttons, messages, constants, error_types


class MenuEventHandler(ABC):
    def __init__(self, menu: MenuManager, sql_tools: SQliteTools):
        self._menu = menu
        self._sql_tools = sql_tools

        self._state: str = ''

    @abstractmethod
    def event_handler(self, event: str) -> MessageConfig:
        pass

    def set_state(self, state: str):
        self._state = state

    def _reset_menu(self, reset_path: str) -> MessageConfig:
        return self._menu.reset_menu(reset_path, buttons.OK, texts.END_RESET_TEXT)

    def _send_menu(self, button_settings: tuple[ButtonSettings, ...],
                   reset_path: str, back_path: str, text_menu: str,
                   parse_mode: str | None = None,
                   additional_keyboard: tuple[tuple[str, str], ...] | None = None) -> MessageConfig:
        self._menu.make_menu_keyboard(button_settings=button_settings,
                                      reset_path=reset_path,
                                      back_path=back_path,
                                      additional_keyboard=additional_keyboard)

        return self._menu.send_menu(text_menu, parse_mode=parse_mode)

    def _create_empty_data_message(self) -> MessageConfig:
        return MessageConfig(button_settings=(ButtonSettings(constants.INTERACTION_MAIN_MENU, buttons.BACK_TEXT),),
                             text_message=texts.NOTHING_FOUND,
                             row_buttons=1)


class FillingEventHandler(MenuEventHandler):
    def __init__(self, menu: MenuManager, sql_tools: SQliteTools, filling_state: FillingContainer,
                 parameters: JsonDictsHandler, back_path: str):
        super().__init__(menu, sql_tools)

        self._filling_state = filling_state
        self._parameters = parameters

        self._back_path = back_path

    def event_handler(self, event: str) -> MessageConfig:
        RESET_PATH = f'interaction.{self._state}/reset'

        if event == 'reset':
            response_message = self._reset_menu(f'interaction.{self._state}')

        elif event.startswith('add'):
            data = self._filling_state.value(self._state)
            if not isinstance(data, tuple):
                data = (data,)

            number_button = self._menu.number_button(event)
            settings = self._menu.group_menu.button_setting(int(number_button))
            new_value = (settings.text,)

            self._filling_state.add_value(self._state, data + new_value)

            response_message = messages.SUCCESSFUL_SAVE_MESSAGE

        else:
            # Start session

            option = self._parameters.get_value(self._state)
            button_settings = self._menu.menu_keyboard('interaction', self._state, 'add', option)

            response_message = self._send_menu(button_settings, RESET_PATH, self._back_path, texts.TEXT_OPERATOR_MENU)

        return response_message


class EditPasswordEventHandler(MenuEventHandler):
    def __init__(self, menu: MenuManager, sql_tools: SQliteTools, passwords: SettingsManager,
                 state_user: StateUserContainer):
        super().__init__(menu, sql_tools)

        self._passwords = passwords
        self._state_user = state_user

    def event_handler(self, event: str) -> MessageConfig:
        response_message = None

        if event == 'start':
            passwords = self._sql_tools.passwords()
            if passwords:
                self._passwords.update_data(passwords)
                response_message = self._send_menu(
                    self._menu.menu_keyboard('interaction', self._state, 'show', self._passwords.names),
                    reset_path='interaction.passwords/reset',
                    back_path='interaction.main||group_exit',
                    text_menu=texts.TEXT_EDIT_PASSWORD_MENU,
                    additional_keyboard=(buttons.RESET_PASSWORDS,)
                    )
            else:
                response_message = self._create_empty_data_message()

        elif event == 'reset_passwords':
            pass

        elif event == 'reset':
            response_message = self._reset_menu('interaction.passwords/start')

        elif event.startswith('show'):
            number_button = self._menu.number_button(event)
            index_password = self._menu.restore_menu_button(number_button)

            self._passwords.remembered_data(self._passwords.get_key(index_password))

            password_data = self._passwords.remember_data

            response_message = MessageConfig(button_settings=(ButtonSettings('interaction.passwords/edit',
                                                                             texts.EDIT_BUTTON_TEXT),
                                                              ButtonSettings('interaction.passwords/start',
                                                                             buttons.BACK_TEXT)),
                                             text_message=f'Должность: {password_data.name}, '
                                                          f'пароль: ||{password_data.value}||',
                                             row_buttons=1,
                                             parse_mode=constants.PARSE_MODE1
                                             )
        elif event.startswith('edit'):
            self._state_user.update_state('input password')
            response_message = messages.INPUT_NEW_PASSWORD

        return response_message


class BlackListEventHandler(MenuEventHandler):
    def __init__(self, menu: MenuManager, sql_tools: SQliteTools, black_list: BlackListManager):
        super().__init__(menu, sql_tools)

        self._black_list = black_list

    def event_handler(self, event: str) -> MessageConfig:
        response_message = None

        if event == 'start':
            black_users = self._sql_tools.black_users()

            if black_users:
                self._black_list.update_users(black_users)
                response_message = self._send_menu(
                    self._menu.menu_keyboard('interaction', self._state, 'show', self._black_list.names),
                    reset_path='interaction.black_list/reset',
                    back_path='interaction.main||group_exit',
                    text_menu=texts.TEXT_EDIT_BLACK_LIST_MENU,
                    additional_keyboard=(buttons.RESET_BLACK_LIST,))
            else:
                response_message = self._create_empty_data_message()

        elif event == 'reset':
            response_message = self._reset_menu('interaction.black_list/start')

        elif event == 'reset_table':
            pass

        elif event.startswith('show'):
            number_button = self._menu.number_button(event)
            index_user = self._menu.restore_menu_button(number_button)

            self._black_list.remember_user(index_user)

            response_message = MessageConfig(button_settings=(
                ButtonSettings('interaction.black_list/delete', buttons.DELETE_FROM_BLACK_LIST_TEXT),
                ButtonSettings('interaction.black_list/start', buttons.BACK_TEXT)),
                text_message=self._black_list.string_data_remember_user,
                row_buttons=1)

        elif event == 'delete':
            self._sql_tools.delete_user(self._black_list.remembered_user.id)

            response_message = messages.SUCCESSFUL_DELETE_USER

        return response_message


class ParametersEditEventHandler(MenuEventHandler):
    def __init__(self, menu: MenuManager, sq_tools: SQliteTools, parameters: SettingsManager):
        super().__init__(menu, sq_tools)

        self._parameters = parameters

        self._number_button_group = None

    def event_handler(self, event: str) -> MessageConfig:
        response_message = None

        if event == 'start':
            parameters = self._sql_tools.parameters()
            if parameters:
                self._parameters.update_data(parameters)

                response_message = self._send_menu(button_settings=self._menu.menu_keyboard('interaction', self._state,
                                                                                            'show-group',
                                                                                            self._parameters.names),
                                                   reset_path='interaction.parameters/reset',
                                                   back_path='interaction.main||group_exit',
                                                   text_menu=texts.TEXT_EDIT_PARAMETERS,
                                                   additional_keyboard=buttons.PARAMETERS_ADDITIONAL_KEYBOARD)
            else:
                response_message = self._create_empty_data_message()

        elif event == 'reset':
            response_message = self._reset_menu('interaction.parameters/start')

        elif event == 'reset_par':
            pass

        elif event == 'add':
            pass

        elif event.startswith('show-group'):
            self._number_button_group = self._menu.number_button(event)
            index_group = self._menu.restore_menu_button(self._number_button_group)

            self._parameters.remembered_data(self._parameters.get_key(index_group))
            parameter = self._parameters.remember_data

            response_message = self._send_menu(
                self._menu.menu_keyboard('interaction', self._state, 'show-parameter', parameter.value),
                reset_path='interaction.parameters/reset',
                back_path=f'interaction.parameters/start',
                text_menu=texts.TEXT_SHOW_GROUP_PARAMETERS
                )

        elif event.startswith('show-parameter'):
            number_button = self._menu.number_button(event)
            index_parameter = self._menu.restore_menu_button(number_button)

            parameter = self._parameters.remember_data.value[index_parameter]

            response_message = MessageConfig(button_settings=
                                             (ButtonSettings('interaction.parameters/delete',
                                                             buttons.DELETE_FROM_BLACK_LIST_TEXT),
                                              ButtonSettings(
                                                  f'interaction.parameters/show-group_{self._number_button_group}',
                                                  buttons.BACK_TEXT)),
                                             row_buttons=1,
                                             text_message=parameter)

        elif event == 'delete':
            self._sql_tools.delete_parameter(self._parameters.remember_key)

            response_message = MessageConfig(button_settings=
                                             (ButtonSettings(
                                                 f'interaction.parameters/show-group_{self._number_button_group}',
                                                 buttons.BACK_TEXT),),
                                             row_buttons=1,
                                             text_message=texts.TEXT_DELETE_PARAMETER)

        return response_message


class MenuContext:
    def __init__(self):
        self._strategy = None

    def set_strategy(self, strategy: MenuEventHandler):
        if not isinstance(strategy, MenuEventHandler):
            raise error_types.WrongType(str(type(strategy)))

        if self._strategy != strategy:
            self._strategy = strategy

    def __not_strategy_error(self):
        if not self._strategy:
            raise error_types.CleanData('Strategy', 'None')

    @property
    def get_strategy(self):
        return self._strategy

    def event_handler(self, event: str) -> MessageConfig:
        self.__not_strategy_error()
        return self._strategy.event_handler(event)

    def set_state(self, state: str):
        self.__not_strategy_error()
        self._strategy.set_state(state)


menu_context = MenuContext()
