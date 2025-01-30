from abc import abstractmethod, ABC

from constants import messages, constants, texts, buttons
from containers.bot_containers import MessageConfig, CallBackData, StateUserContainer, ButtonSettings
from filling_inputs import FillingInputs
from menu_hanlders import FillingEventHandler, EditPasswordEventHandler, BlackListEventHandler, \
    ParametersEditEventHandler, MenuContext
from sq_functions import SQliteTools
from data_management import FillingContainer
from json_storage import JsonDictsHandler

from visual import Visual
from bot_tools import PhotoManager, MenuManager

from data_management import SettingsManager, BlackListManager


class FillingInputsMethods:
    def date_input(self, parameter: str, text_message: str) -> MessageConfig:
        raise ValueError('the strategy does not use the interaction filling!')

    def int_input(self, parameter: str, text_message: str) -> MessageConfig:
        raise ValueError('the strategy does not use the interaction filling!')


class InteractionFilling(FillingInputsMethods):
    def __init__(self, filling_state: FillingContainer, state_user: StateUserContainer):
        self.__filling_state = filling_state
        self.__state_user = state_user

    def _make_menu(self) -> MessageConfig:
        return MessageConfig()

    def _filling_menu(self) -> MessageConfig:
        self.__state_user.update_state('not_input')
        return self._make_menu()

    def _keyboard_filling(self, is_status=True) -> list[ButtonSettings, ...]:
        b_setting = []
        for new_callback, container in self.__filling_state.data.items():
            b_setting.append(ButtonSettings(CallBackData.creating_callback('interaction', new_callback),
                                            f'{container.name} {container.status if is_status else ""}'))

        return b_setting

    def _save_filling_data(self, value: any, name: str):
        self.__filling_state.add_value(name, value)

        return messages.SUCCESSFUL_SAVE_MESSAGE

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


class InteractionHandler(FillingInputsMethods, ABC):
    def __init__(self, state_user: StateUserContainer):
        self._state_user = state_user

    @abstractmethod
    async def interaction(self, callback: CallBackData) -> MessageConfig:
        pass


class DataOperatorInteraction(InteractionFilling, InteractionHandler):
    def __init__(self, state_user: StateUserContainer, menu: MenuManager,
                 sql_tools: SQliteTools, parameters_json: JsonDictsHandler):
        self._filling_state = FillingContainer(constants.FILLING_OPERATOR_MENU)

        InteractionFilling.__init__(self, self._filling_state, state_user)
        InteractionHandler.__init__(self, state_user)

        self._sql_tools = sql_tools

        self._menu = FillingEventHandler(menu, sql_tools, self._filling_state, parameters_json,
                                         f'{constants.INTERACTION_MAIN_MENU}||group_exit')
        self._operator_inputs = FillingInputs(self._filling_state, self._state_user, self._menu,
                                              constants.INTERACTION_MAIN_MENU, messages.RATING_SLIDER,
                                              messages.DATA_OPERATOR_INPUT_PROMPTS)

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

        elif callback.state in self._operator_inputs:
            response_message = self._operator_inputs.filling_interaction(callback.state, callback.event)

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


class AnalystInteraction(InteractionFilling, InteractionHandler):
    def __init__(self, state_user: StateUserContainer, visual: Visual, photos_manager: PhotoManager, menu: MenuManager,
                 sql_tools: SQliteTools, parameters_json: JsonDictsHandler):
        self._filling_state = FillingContainer(constants.FILLING_ANALYST_MENU)

        InteractionFilling.__init__(self, self._filling_state, state_user)
        InteractionHandler.__init__(self, state_user)

        self.visual = visual
        self.photos = photos_manager

        self.analyst_setting_menu = FillingEventHandler(menu, sql_tools, self._filling_state,
                                                        parameters_json, 'interaction.edit/group_exit')

        self.analyst_inputs = FillingInputs(self._filling_state, state_user, self.analyst_setting_menu,
                                            'interaction.edit', messages.CAPACITY_SLIDER)

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

        elif callback.state in self.analyst_inputs:
            response_message = self.analyst_inputs.filling_interaction(callback.state, callback.event)

        else:
            raise ValueError(f'Wrong state: {callback.state}!')

        return response_message


class AdminInteraction(InteractionHandler):
    def __init__(self, state_user: StateUserContainer, menu_context: MenuContext, menu: MenuManager,
                 sql_tools: SQliteTools, ):
        super().__init__(state_user)

        self._menu_context = menu_context

        self._passwords = SettingsManager()
        self.black_list = BlackListManager()
        self.parameters = SettingsManager()

        self.STRATEGY_MENU_ADMIN_HANDLERS = {
            'passwords': EditPasswordEventHandler(menu, sql_tools, self._passwords, state_user),
            'black_list': BlackListEventHandler(menu, sql_tools, self.black_list),
            'parameters': ParametersEditEventHandler(menu, sql_tools, self.parameters)
        }

    async def interaction(self, callback: CallBackData) -> MessageConfig:
        response_message = MessageConfig()

        if callback.state == 'main':
            response_message = messages.ADMIN_MENU

        elif callback.state in self.STRATEGY_MENU_ADMIN_HANDLERS.keys():
            handler_strategy = self.STRATEGY_MENU_ADMIN_HANDLERS.get(callback.state)

            self._menu_context.set_strategy(handler_strategy)

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

    def __eq__(self, other):
        return other is self._strategy_interaction
