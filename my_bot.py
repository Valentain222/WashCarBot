from constants import texts, messages

from aiogram import types

from visual import Visual
from sq_functions import sql_connect

from containers import MessageConfig, StateUserContainer, CallBackData
from bot_tools import MenuManager, PhotoManager, TextManager

from menu_hanlders import MenuContext

from json_storage import JsonDictsHandler

import sq_functions

from interaction import InteractionContext, DataOperatorInteraction, AnalystInteraction, AdminInteraction


# ↩
class MYBot:
    parameters_json = JsonDictsHandler('parameters.json')

    def __init__(self, user_id):
        self.user_id = user_id

        self.wrong_password_counter = 0

        self.sql_tools: sq_functions.SQliteTools = sql_connect
        self.menu = MenuManager()
        self.bot = TextManager()
        self.photos = PhotoManager(self.bot)
        self.visual = Visual()
        self.state_user = StateUserContainer()

        self.menu_context = MenuContext()
        self.interaction_context = InteractionContext()

        self.data_operator_interaction = DataOperatorInteraction(self.state_user, self.menu,
                                                                 self.sql_tools, self.parameters_json)
        self.analyst_interaction = AnalystInteraction(self.state_user, self.visual, self.photos, self.menu,
                                                      self.sql_tools, self.parameters_json)
        self.admin_interaction = AdminInteraction(self.state_user, self.menu_context, self.menu, self.sql_tools)

        self.INTERACTION_STRATEGIES = {
            'data_operator': self.data_operator_interaction,
            'analyst':  self.analyst_interaction,
            'admin': self.admin_interaction
        }

        self.USER_INPUTS = {
            'filling date': self.interaction_context.date_filling,
            'filling int': self.interaction_context.int_filling
        }

    async def help(self, message: types.Message):
        pass

    async def state_command(self, message: types.Message):
        command = message.text

        await self.__content_clear()
        await self.__chat_clear()
        await self.bot.delete_message(message.chat.id, message.message_id)

        if not self.bot.bots_message:
            self.bot.bots_message = message
            self.bot.config_bots_message.update_config(messages.UNEXPECTED_MESSAGE_RECEIVED_BEFORE_START)

        if command == '/restore' and self.photos.photos:
            await self.photos.send_photos(is_loading_message=False)

        try:
            if command == '/reset':
                self.state_user.clear()
                self.bot.config_bots_message.update_config(messages.UNEXPECTED_MESSAGE_RECEIVED_BEFORE_START)

            await self.bot.send_message(self.bot.config_bots_message.configs, True, False)
        except Exception as e:
            print(e)

    async def start(self, message: types.Message):

        """Handler for /start"""

        create_new_message = False if self.bot.bots_message else True
        if create_new_message:
            self.bot.bots_message = message

        await self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        message_data = self.__is_user_in_black_list(message.from_user.id)
        await self.bot.send_message(message=message_data, is_new_m=create_new_message)

    # -----------------------

    async def basic_callback_center(self, callback: CallBackData):
        response_message: MessageConfig() = None
        is_spawn_new = False

        if callback.state == 'main_menu':
            # Making main menu
            self.state_user.clear()
            response_message = messages.MAIN_MENU

        elif callback.state in ('analyst', 'data_operator', 'admin'):
            # Loging in

            self.state_user.update_state('log_in')
            self.state_user.update_user(callback.state)
            response_message = messages.DATA_LOG_IN_MESSAGE

        elif callback.state == 'back':
            # Backing on one step

            spawn = False

            if spawn:
                is_spawn_new = True
                await self.bot.delete_message(chat_id=self.bot.bots_message.chat.id,
                                              message_id=self.bot.bots_message.message_id)
            response_message = self.bot.prev_config_bots_message.configs

        else:
            raise ValueError('Wrong callback!')

        await self.bot.send_message(message=response_message, is_new_m=is_spawn_new)

    async def interaction_entry_point(self, callback: CallBackData):
        interaction_strategy = self.INTERACTION_STRATEGIES.get(self.state_user.user)
        if interaction_strategy:
            if interaction_strategy != self.interaction_context:
                self.interaction_context.set_interaction_strategy(interaction_strategy)
            response_message = await self.interaction_context.interaction_handler(callback)
        else:
            raise ValueError(f'Wrong strategy name! Available {self.INTERACTION_STRATEGIES.keys()}')

        await self.bot.send_message(message=response_message, is_new_m=False)

    async def parallel_actions(self, callback: CallBackData):
        if callback.parallel_action:
            if callback.parallel_action == 'group_exit':
                await self.__content_clear()
            else:
                raise ValueError(f'Wrong parallel action {callback.parallel_action}!')

    async def menu_operations(self, callback: CallBackData):
        response_message = None

        if callback.state == 'browsing':
            response_message = self.menu.browsing(callback.event, self.bot.config_bots_message.configs.text,
                                                  self.bot.config_bots_message.configs.parse_mode)

        elif callback.state == 'search':
            if self.menu.prev_group_menu_settings:
                for setting in self.menu.prev_group_menu_settings:
                    self.menu.group_menu.append(setting)

            response_message = messages.SEARCH_INPUT_PROMPTS
            self.state_user.update_state('search')

        await self.bot.send_message(response_message, is_new_m=False)

    # -----------

    async def user_input(self, message: types.message):
        state = ''
        user = ''
        response_message = None

        is_send_new = False
        if not self.bot.bots_message:
            is_send_new = True
            self.bot.bots_message = message

        if self.state_user:
            state, user = self.state_user.state, self.state_user.user
        text_message = message.text

        if not state or state == 'not_input':
            if not is_send_new:
                response_message = messages.UNEXPECTED_MESSAGE_RECEIVED_AFTER_START
            else:
                response_message = messages.UNEXPECTED_MESSAGE_RECEIVED_BEFORE_START

        elif 'filling' in state:
            if ':' in state:
                if len((settings := state.split(':'))) == 2:
                    input_type, parameter = settings
                    if input_type in self.USER_INPUTS.keys():
                        response_message = self.USER_INPUTS[input_type](parameter, text_message)
                    else:
                        raise ValueError(f'Wrong input type {input_type}!')
                else:
                    raise ValueError(f'Wrong number of parameters in filling {settings}!')
            else:
                raise ValueError(f'Wrong filling state: {state}!')

        elif state == 'input password':
            self.sql_tools.save_password(self.admin_interaction.passwords.remember_key, text_message)
            response_message = messages.SAVE_PASSWORD

        elif state == 'search':
            # Search data

            if self.menu.group_menu:
                button_settings = self.menu.group_menu.search(text_message)
                self.menu.prev_group_menu_settings = self.menu.group_menu.settings

                if button_settings:
                    self.menu.make_menu_keyboard(button_settings, self.menu.group_menu.reset_path,
                                                 self.menu.group_menu.back_path)
                    text = texts.SUCCESS_SEARCH_TEXT
                else:
                    self.menu.group_menu.clear()
                    text = texts.FAILURE_SEARCH_TEXT

                text += f' по запросу: {text_message}'
                response_message = self.menu.send_menu(text)

            self.state_user.update_state('not_input')

        elif state == 'log_in':
            # Check password
            password = self.sql_tools.fetch_password(post=user)

            if password == text_message:
                response_message = messages.DATA_TRUTH_PASSWORD_MESSAGE
                self.wrong_password_counter = 0
                self.state_user.update_state('not_input')
            else:
                is_attempts_end, response_message = self.__fail_count()
                if not is_attempts_end:
                    self.state_user.clear()
                    self.sql_tools.add_to_black_list(self.user_id, message.from_user.username)

        else:
            raise ValueError(f'Wrong state: {state}')

        await self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await self.bot.send_message(response_message, is_send_new)

    # --------

    async def __content_clear(self):
        if self.photos.photos:
            await self.photos.del_photos(reset=False)
        if self.menu:
            self.menu.exit_menu()

    async def __chat_clear(self):
        if self.bot.bots_message:
            try:
                await self.bot.delete_message(self.bot.bots_message.chat.id, self.bot.bots_message.message_id)
            except Exception as e:
                print('sss', e)

    def __is_user_in_black_list(self, user_id):

        black_mark = False
        if not black_mark:
            return messages.DATA_START_SUCCESS_MENU
        else:
            return messages.BLACK_USER

    def __failed_attempt_text(self) -> str:
        return texts.FAILED_ATTEMPT_INPUT_PASSWORD.replace('counter', f'{abs(self.wrong_password_counter-10)}')

    def __fail_count(self) -> tuple[bool, MessageConfig]:
        if self.wrong_password_counter == 9:
            self.wrong_password_counter = 0
            return False, messages.BLACK_USER

        self.wrong_password_counter += 1
        return True, MessageConfig(text_message=self.__failed_attempt_text())
