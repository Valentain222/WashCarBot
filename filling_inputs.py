from data_management import FillingContainer

from constants import texts, constants, buttons, error_types

from menu_hanlders import menu_context, MenuEventHandler

from datetime import date

from containers.bot_containers import MessageConfig, StateUserContainer, ButtonSettings


class FillingInputs:
    def __init__(self, filling_container: FillingContainer, state_user: StateUserContainer,
                 menu_handler: MenuEventHandler, main_path: str, slider_message: MessageConfig = None,
                 input_int_message: MessageConfig = None):
        self._filling_container = filling_container
        self._state_user = state_user
        self._menu_handler = menu_handler

        self._SLIDER_MESSAGE = slider_message
        self._INPUT_INT_MESSAGE = input_int_message
        self._MAIN_PATH = main_path

        self._INPUTS_HANDLERS = {
            'int': self.__input_int,
            'menu': self.__input_menu,
            'slider': self.__input_slider,
            'date': self.__input_date
        }

    def __contains__(self, item):
        return item in self._filling_container.data.keys()

    def filling_interaction(self, state, event) -> MessageConfig:
        type_input = self._filling_container.data.get(state).type_input

        handler = self._INPUTS_HANDLERS.get(type_input, False)

        if not handler:
            raise error_types.InvalidError('input type', type_input, ', '.join(self._INPUTS_HANDLERS.keys()))

        return handler(state, event)

    def set_slider(self, slider_message: MessageConfig):
        self._SLIDER_MESSAGE = slider_message

    def set_input_int_message(self, input_int_message: MessageConfig):
        self._INPUT_INT_MESSAGE = input_int_message

    def __input_int(self, state: str, event: str) -> MessageConfig:
        if self._INPUT_INT_MESSAGE is None:
            raise error_types.CleanData('Input message')
        print(state)
        self._state_user.update_state(f'filling int:{state}')

        return self._INPUT_INT_MESSAGE

    def __input_menu(self, state: str, event: str) -> MessageConfig:
        menu_context.set_strategy(self._menu_handler)

        menu_context.set_state(state)
        return menu_context.event_handler(event)

    def __input_slider(self, state: str, event: str) -> MessageConfig:
        if self._SLIDER_MESSAGE is None:
            raise error_types.CleanData('Slider message', 'None')

        if 'save' in event:
            value = event[-1]
            response_message = self.__save_filling_data(value, state, self._filling_container)
        else:
            response_message = self._SLIDER_MESSAGE

        return response_message

    def __input_date(self, state: str, event: str) -> MessageConfig:
        if event:
            if event == 'auto':
                # Today date

                input_date = date.today()
                response_message = self.__save_filling_data(input_date, state, self._filling_container)

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

    def __save_filling_data(self, value: any, name: str, filling_class: FillingContainer):
        filling_class.add_value(name, value)

        return MessageConfig(button_settings=(ButtonSettings(self._MAIN_PATH, buttons.SUCCESSFUL_SAVING_TEXT),),
                             row_buttons=1,
                             text_message=texts.SUCCESSFUL_SAVING_TEXT,
                             parse_mode=constants.PARSE_MODE1)

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
