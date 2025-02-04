from abc import abstractmethod, ABC
from datetime import date

from constants import messages, constants, texts, buttons, error_types
from containers.bot_containers import MessageConfig, CallBackData, StateUserContainer, ButtonSettings
from menu_hanlders import FillingEventHandler, EditPasswordEventHandler, BlackListEventHandler, \
    ParametersEditEventHandler, MenuContext, MenuEventHandler
from sq_functions import SQliteTools
from data_management import FillingManager
from json_storage import JsonDictsHandler

from visual import Visual
from interactive_tools import PhotoManager, MenuManager

from data_management import SettingsManager, BlackListManager


class InputsMethods:
    def date_input(self, parameter: str, text_message: str) -> MessageConfig:
        raise ValueError('the strategy does not use the interaction filling!')

    def int_input(self, parameter: str, text_message: str) -> MessageConfig:
        raise ValueError('the strategy does not use the interaction filling!')

    def str_input(self, parameter: str, text_message: str) -> MessageConfig:
        raise ValueError('the strategy does not use the interaction filling!')


class InputHandler(InputsMethods):
    def __init__(self, state_user: StateUserContainer, filling_container: FillingManager, exit_path: str,
                 menu_handler: MenuEventHandler = None, slider_message: MessageConfig = None,
                 input_int_message: MessageConfig = None, input_str_message: MessageConfig = None):
        self._state_user = state_user
        self._filling_container = filling_container

        self._menu_handler = menu_handler
        self._SLIDER_MESSAGE = slider_message
        self._INPUT_INT_MESSAGE = input_int_message
        self._MAIN_PATH = exit_path
        self._INPUT_STR_MESSAGE = input_str_message

        self._INPUTS_HANDLERS = {
            'int': self.__input_int,
            'menu': self.__input_menu,
            'slider': self.__input_slider,
            'date': self.__input_date
        }

    def _save_filling_data(self, value: any, name: str) -> MessageConfig:
        self._filling_container.add_value(name, value)

        return MessageConfig(button_settings=(ButtonSettings(self._MAIN_PATH, buttons.SUCCESSFUL_SAVING_TEXT),),
                             row_buttons=1,
                             text_message=texts.SUCCESSFUL_SAVING_TEXT,
                             parse_mode=constants.PARSE_MODE1)

    def input_handler(self, state, event) -> MessageConfig:
        type_input = self._filling_container.data.get(state).type_input

        handler = self._INPUTS_HANDLERS.get(type_input, False)

        if not handler:
            raise error_types.InvalidError('input type', type_input, ', '.join(self._INPUTS_HANDLERS.keys()))

        return handler(state, event)

    def __input_str(self, state: str, event: str):
        if self._INPUT_INT_MESSAGE is None:
            raise error_types.CleanData('Input str message')
        self._state_user.update_state(f'filling str:{state}')

        return self._INPUT_STR_MESSAGE

    def __input_int(self, state: str, event: str) -> MessageConfig:
        if self._INPUT_INT_MESSAGE is None:
            raise error_types.CleanData('Input message')
        self._state_user.update_state(f'filling int:{state}')

        return self._INPUT_INT_MESSAGE

    def __input_menu(self, state: str, event: str) -> MessageConfig:
        return self._menu_handler.event_handler(event)

    def __input_slider(self, state: str, event: str) -> MessageConfig:
        if self._SLIDER_MESSAGE is None:
            raise error_types.CleanData('Slider message', 'None')

        if 'save' in event:
            value = event[-1]
            response_message = self._save_filling_data(value, state)
        else:
            response_message = self._SLIDER_MESSAGE

        return response_message

    def __input_date(self, state: str, event: str) -> MessageConfig:
        if event:
            if event == 'auto':
                # Today date

                input_date = date.today()
                response_message = self._save_filling_data(input_date, state)

            elif event == 'manual':
                # Input date

                self._state_user.update_state(f'filling date:{state}')
                response_message = self.__manual_input_date(state)
            else:
                raise error_types.WrongEvent(event)
        else:
            # Make selection menu
            response_message = self.__main_input_date_menu(state)

        return response_message

    def __main_input_date_menu(self, state) -> MessageConfig:
        return MessageConfig(button_settings=(
            ButtonSettings(f"interaction.{state}/manual", buttons.DATE_MANUAL_INPUT_TEXT),
            ButtonSettings(f"interaction.{state}/auto", buttons.DATE_AUTO_INPUT_TEXT),
            ButtonSettings(self._MAIN_PATH, buttons.BACK_TEXT)),
            row_buttons=1,
            text_message=texts.MAIN_INPUT_DATE_TEXT,
            parse_mode=constants.PARSE_MODE1)

    def __manual_input_date(self, state) -> MessageConfig:
        return MessageConfig(button_settings=(ButtonSettings(f'interaction.{state}', buttons.BACK_TEXT),),
                             row_buttons=1,
                             text_message=texts.MANUAL_INPUT_DATE_TEXT,
                             parse_mode=constants.PARSE_MODE1)

    def _make_menu(self) -> MessageConfig:
        return MessageConfig()

    def _filling_menu(self) -> MessageConfig:
        self._state_user.update_state('not_input')
        return self._make_menu()

    def _keyboard_filling(self, is_status=True) -> list[ButtonSettings, ...]:
        b_setting = []
        for new_callback, container in self._filling_container.data.items():
            b_setting.append(ButtonSettings(CallBackData.creating_callback('interaction', new_callback),
                                            f'{container.name} {container.status if is_status else ""}'))

        return b_setting

    def date_input(self, parameter: str, text_message: str) -> MessageConfig:
        if constants.DATE_PATTERN.fullmatch(text_message):
            response_message = self._save_filling_data(text_message, parameter)
        else:
            response_message = messages.WRONG_INPUT_DATE_MESSAGE

        return response_message

    def int_input(self, parameter: str, text_message: str) -> MessageConfig:
        if text_message.isdigit():
            response_message = self._save_filling_data(text_message, parameter)
        else:
            response_message = messages.WRONG_INPUT_PROMPTS_MESSAGE

        return response_message

    def str_input(self, parameter: str, text_message: str) -> MessageConfig:
        self._save_filling_data(text_message, parameter)

        return messages.SUCCESSFUL_SAVE_MESSAGE


class InteractionHandler(InputsMethods, ABC):
    def __init__(self, state_user: StateUserContainer):
        self._state_user = state_user

    @abstractmethod
    async def interaction(self, callback: CallBackData) -> MessageConfig:
        pass


class DataOperatorInteraction(InputHandler, InteractionHandler):
    def __init__(self, state_user: StateUserContainer, menu: MenuManager,
                 sql_tools: SQliteTools, parameters_json: JsonDictsHandler):
        self._filling_state = FillingManager(constants.FILLING_OPERATOR_MENU)

        self._menu = FillingEventHandler(menu, sql_tools, self._filling_state, parameters_json,
                                         f'{constants.INTERACTION_MAIN_MENU}||group_exit')
        InputHandler.__init__(self,
                              state_user,
                              self._filling_state,
                              constants.INTERACTION_MAIN_MENU, self._menu,
                              messages.RATING_SLIDER,
                              messages.DATA_OPERATOR_INPUT_PROMPTS
                              )
        InteractionHandler.__init__(self, state_user)

        self._sql_tools = sql_tools

    def _make_menu(self) -> MessageConfig:
        text_message = texts.TEXT_DATA_OPERATOR_MAIN_MENU
        b_setting = self._keyboard_filling()
        b_setting.append(ButtonSettings('interaction.send', buttons.SEND))

        return MessageConfig(button_settings=(tuple(b_setting), (buttons.BACK_MAIN_MENU,)), row_buttons=(2, 1),
                             text_message=text_message, parse_mode=constants.PARSE_MODE1)

    async def interaction(self, callback: CallBackData) -> MessageConfig:
        response_message = None

        if callback.state == 'main':
            # Making main operators menu
            response_message = self._filling_menu()

        elif callback.state in self._filling_state.data.keys():
            self._menu.set_state(callback.state)
            response_message = self.input_handler(callback.state, callback.event)

        elif callback.state == 'send':
            is_filled = self._filling_state.is_filled
            if is_filled:
                data = self._filling_state.data

                try:
                    self._sql_tools.save_data(data)
                except ValueError as e:
                    print(e)
                self._filling_state.reset()

                response_message = messages.SUCCESSFUL_SEND_MESSAGE
            else:
                response_message = messages.DATA_OPERATOR_FILLED_FAILURE

        else:
            raise ValueError('Wrong State!!')

        return response_message


class AnalystInteraction(InputHandler, InteractionHandler):
    def __init__(self, state_user: StateUserContainer, visual: Visual, photos_manager: PhotoManager, menu: MenuManager,
                 sql_tools: SQliteTools, parameters_json: JsonDictsHandler):
        self._filling_state = FillingManager(constants.FILLING_ANALYST_MENU)

        self.analyst_setting_menu = FillingEventHandler(menu, sql_tools, self._filling_state,
                                                        parameters_json, 'interaction.edit/group_exit')
        InputHandler.__init__(self,  state_user, self._filling_state,
                              'interaction.edit', self.analyst_setting_menu, messages.CAPACITY_SLIDER)
        InteractionHandler.__init__(self, state_user)

        self.visual = visual
        self.photos = photos_manager

    def _make_menu(self) -> MessageConfig:
        button_settings = self._keyboard_filling(is_status=False)

        return MessageConfig(button_settings=(tuple(button_settings),
                                              (ButtonSettings(constants.INTERACTION_MAIN_MENU,
                                                              buttons.BACK_TEXT),)),
                             row_buttons=(2, 1),
                             text_message=texts.TEXT_ANALYST_SETTINGS_MENU)

    async def interaction(self, callback: CallBackData) -> MessageConfig:
        response_message: MessageConfig = MessageConfig()

        if callback.state == 'main':
            response_message = messages.ANALYST_MAIN_MENU

        elif callback.state == 'open':
            self.visual.set_settings(self._filling_state)
            self.photos.photos.set_paths(self.visual.generate_plots())
            await self.photos.send_photos()

            response_message = MessageConfig(text_message=texts.ANALYST_OPEN_STATIC,
                                             button_settings=buttons.PLOTS_MENU_BUTTON,
                                             row_buttons=1)

        elif callback.state == 'edit':
            response_message = self._filling_menu()

        elif callback.state in self._filling_state.data.keys():
            response_message = self.input_handler(callback.state, callback.event)

        else:
            raise ValueError(f'Wrong state: {callback.state}!')

        return response_message


class AdminInteraction(InteractionHandler):
    def __init__(self, state_user: StateUserContainer, menu_context: MenuContext, menu: MenuManager,
                 sql_tools: SQliteTools, ):
        super().__init__(state_user)
        self._sql_tools = sql_tools

        self._menu_context = menu_context

        self._passwords = SettingsManager()
        self.black_list = BlackListManager()
        self.parameters = SettingsManager()

        self._str_strategy: str = ''

        self.STRATEGY_MENU_ADMIN_HANDLERS = {
            'passwords': EditPasswordEventHandler(menu, sql_tools, self._passwords, state_user),
            'black_list': BlackListEventHandler(menu, sql_tools, self.black_list),
            'parameters': ParametersEditEventHandler(state_user, menu, sql_tools, self.parameters)
        }

        self.STR_INPUTS = {
            'input password': self.__input_password,
            'parameter': self.__input_new_parameter
        }

    def __input_password(self, parameter: str, text_message: str) -> MessageConfig:
        self._sql_tools.save_password(self._passwords.remember_key, text_message)
        return messages.SAVE_PASSWORD

    def __input_new_parameter(self, parameter: str, text_message: str) -> MessageConfig:
        self._sql_tools.add_parameter(text_message)
        return messages.SUCCESSFUL_NEW_PARAMETER

    def str_input(self, parameter: str, text_message: str) -> MessageConfig:
        str_input_def = self.STR_INPUTS.get(parameter)

        if str_input_def is None:
            raise ValueError(f'Wrong parameter {parameter}!')

        # noinspection PyArgumentList
        return str_input_def(parameter, text_message)

    async def interaction(self, callback: CallBackData) -> MessageConfig:
        response_message = MessageConfig()

        if callback.state == 'main':
            response_message = messages.ADMIN_MENU

        elif callback.state in self.STRATEGY_MENU_ADMIN_HANDLERS.keys():
            handler_strategy = self.STRATEGY_MENU_ADMIN_HANDLERS.get(callback.state)

            self._menu_context.set_strategy(handler_strategy)
            self._str_strategy = callback.state

            self._menu_context.set_state(callback.state)
            response_message = self._menu_context.event_handler(callback.event)

        else:
            raise ValueError(f'Wrong state {callback.state}!')

        return response_message

    @property
    def passwords(self):
        return self._passwords


class InteractionContext:
    def __init__(self):
        self._strategy_interaction: InteractionHandler | None = None

    def set_interaction_strategy(self, new_strategy: InteractionHandler):
        self._strategy_interaction = new_strategy

    async def interaction_handler(self, callback: CallBackData) -> MessageConfig:
        return await self._strategy_interaction.interaction(callback)

    def int_filling(self, parameter: str, text_message: str) -> MessageConfig:
        return self._strategy_interaction.int_input(parameter, text_message)

    def date_filling(self, parameter: str, text_message: str) -> MessageConfig:
        return self._strategy_interaction.date_input(parameter, text_message)

    def str_filling(self, parameter: str, text_message: str) -> MessageConfig:
        return self._strategy_interaction.str_input(parameter, text_message)

    def __eq__(self, other):
        return other is self._strategy_interaction
