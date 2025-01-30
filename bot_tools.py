from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from constants import buttons, texts, messages, constants, errors, error_types

from aiogram.exceptions import TelegramBadRequest

from aiogram.types import InputMediaPhoto, FSInputFile
from bot_setup import bot
from aiogram import types
import re

from containers.msg_mgmt_containers import GroupMessagesContainer, MenuGroupContainer, MessageConfig, PhotoContainer
from containers.bot_containers import ButtonSettings, CallBackData


class TextManager:
    def __init__(self):
        self.bots_message = None

        self.config: MessageConfig | None = None
        self.prev_config: MessageConfig | None = None

    @staticmethod
    def make_keyboard(button_settings: tuple[tuple[ButtonSettings, ...]],
                      row_keyboards: tuple) -> types.inline_keyboard_markup:
        keyboard = InlineKeyboardBuilder()

        for button_setting, row_keyboard in zip(button_settings, row_keyboards):
            for i in range(0, len(button_setting), row_keyboard):
                row = button_setting[i:i + row_keyboard]
                keyboard.row(*[InlineKeyboardButton(text=settings.text,
                                                    callback_data=settings.callback) for settings in row])

        return keyboard.as_markup()

    async def send_message(self, message: MessageConfig, is_new_m: bool = True, remembered_configs: bool = True):

        """
        :param is_new_m: New or Old message
        :param message: data from class
        :param remembered_configs: should I remember the message settings
        :return: None
        """
        button_setting = message.button_settings
        rows = message.row
        text = message.text
        parse_mode = message.parse_mode

        if is_new_m is False and self.prev_config:
            is_edited_button_settings = button_setting != self.config.button_settings
            is_edited_text = text != self.config.text
        else:
            is_edited_text = True
            is_edited_button_settings = True

        if is_edited_text or is_edited_button_settings:
            if len(button_setting) > 0:
                builder = self.make_keyboard(button_setting, rows)
            else:
                builder = None

            if remembered_configs:
                self.prev_config = self.config
                self.config = message
            if not is_new_m:
                try:
                    self.bots_message = await bot.edit_message_text(chat_id=self.bots_message.chat.id,
                                                                    message_id=self.bots_message.message_id,
                                                                    text=text, reply_markup=builder,
                                                                    parse_mode=parse_mode)
                except TelegramBadRequest as error:
                    print(error)
                    if 'message to edit not found' in str(error):
                        is_new_m = True

            if is_new_m:
                self.bots_message = await bot.send_message(chat_id=self.bots_message.chat.id, text=text,
                                                           reply_markup=builder,
                                                           parse_mode=parse_mode)

    @staticmethod
    async def delete_message(chat_id: int, message_id: int):
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(e)


class PhotoManager:
    def __init__(self, text_manager: TextManager):
        self._messages: list[types.Message] = []
        self._text_manager = text_manager

        self.photos = PhotoContainer()

    async def send_photos(self, is_loading_message=True):
        media = []

        if is_loading_message:
            await self._text_manager.send_message(messages.LOADING_MESSAGE, False)

        for path in self.photos.paths:
            media.append(InputMediaPhoto(media=FSInputFile(path)))

        self._messages = await bot.send_media_group(self._text_manager.bots_message.chat.id, media)

        await self._text_manager.delete_message(self._text_manager.bots_message.chat.id,
                                                self._text_manager.bots_message.message_id)

        if is_loading_message:
            await self._text_manager.send_message(messages.LOADING_MESSAGE, True)

    async def del_photos(self, reset=True):
        for msg in self._messages:
            try:
                await self._text_manager.delete_message(msg.chat.id, msg.message_id)
            except Exception as e:
                print(e)

        if reset:
            self.photos.clear()


class GroupMessageManager:
    def __init__(self, text_manager: TextManager):
        self.group_message = GroupMessagesContainer()

        self.text_manager = text_manager

    async def send_group_message(self):

        """Функция, создающая меню
        для удобной работы с данными"""

        if self.group_message:
            counter = len(self.group_message)

            if counter == 0:
                await self.text_manager.send_message(messages.LOADING_MESSAGE, False)

            for message in self.group_message.configs:
                builder = self.text_manager.make_keyboard(message.button_settings, message.row)
                message_text = f"{counter+1}) {message.text}"
                if message.parse_mode is not None:
                    message_text = re.sub(r'([)-])', r'\\\1', message_text)

                sent_message = await bot.send_message(text=message_text, reply_markup=builder,
                                                      parse_mode=message.parse_mode,
                                                      chat_id=self.text_manager.bots_message.chat.id)
                self.group_message.append(sent_message)
                counter += 1

                if (counter+1) % constants.LEN_GROUP_MESSAGES == 0:
                    break
        else:
            raise ValueError('Messages is clean')

        await bot.delete_message(self.text_manager.bots_message.chat.id, self.text_manager.bots_message.message_id)
        await self.text_manager.send_message(self.text_manager.config, is_new_m=True)

    async def delete_group_message(self, reset=True):
        for message in self.group_message.messages:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if reset:
            self.group_message.stop_session()

    @staticmethod
    def __make_config_messages_list(text_messages: tuple[str], parse_mode: None | str,
                                    keyboard: tuple[tuple[str, str], ...] = (),
                                    row: int = 1) -> tuple[MessageConfig, ...]:
        messages_config = []
        if text_messages:
            if keyboard:
                for text_message, (callback, text_button) in zip(text_messages, keyboard):
                    messages_config.append(MessageConfig(button_settings=(ButtonSettings(callback, text_button),),
                                                         text_message=text_message,
                                                         row_buttons=row,
                                                         parse_mode=parse_mode))
            else:
                for text_message in text_messages:
                    messages_config.append(MessageConfig(text_message=text_message,
                                                         parse_mode=parse_mode))

        return tuple(messages_config)

    def __make_post_group_menu(self, back_path: str, reset_path: str) -> MessageConfig:
        """
        Make menu group messages
        :param back_path: path for exit menu: global_state.your_state/group_exit,
        event always exists and equally group_exit!
        :param reset_path: the path for restarting the session
        :return: configs menu
        """
        menu_buttons = buttons.MESSAGES_GROUP_MENU_BUTTONS if not self.group_message.is_full_sent else ()
        message_config = MessageConfig(text_message=texts.TEXT_MENU_GROUP_MESSAGES,
                                       row_buttons=1,
                                       button_settings=(menu_buttons + (
                                           (reset_path, buttons.RESET_TEXT_GROUP_MENU),
                                           (back_path, buttons.BACK_TEXT_GROUP_MENU))))
        return message_config

    async def start_group_session(self, text_messages: tuple[str], back_path: str, reset_path: str,
                                  parse_mode: None | str = None,
                                  keyboard_setting: tuple[tuple[str, str], ...] = (), row: int = 1) -> MessageConfig:
        """
        Make config for messages
        :param text_messages: text one message in group message
        :param parse_mode: parse mode message in group messages
        :param keyboard_setting: keyboard setting in message in group messages
        :param back_path: callback for menu (back)
        :param reset_path:callback for menu (reset)
        :param row: row keyborad
        :return:menu config and config all messages in group messages
        """
        menu = self.__make_post_group_menu(back_path, reset_path)
        group_messages = self.__make_config_messages_list(text_messages, parse_mode, keyboard_setting, row)

        self.group_message.start_session(group_messages, menu)
        await self.send_group_message()

        return menu


class MenuManager:
    def __init__(self, len_menu: int = constants.LEN_MENU, menu_buttons_row: int = constants.MENU_BUTTONS_ROW,
                 menu_row: int = constants.MENU_ROW):
        self.group_menu = MenuGroupContainer(len_menu)
        self.prev_group_menu_settings = ()
        
        self.MENU_BUTTONS_ROW = menu_buttons_row
        self.MENU_ROW = menu_row

    def make_menu_keyboard(self, button_settings: tuple[ButtonSettings, ...], reset_path: str, back_path: str,
                           additional_keyboard: tuple[tuple[str, str], ...] | None = None):
        self.group_menu.clear()
        if button_settings:
            for button_setting in button_settings:
                self.group_menu.append(button_setting)
        else:
            raise errors.WRONG_MENU_KEYBOARD_DATA

        self.group_menu.add_back_path(back_path)
        self.group_menu.add_reset_path(reset_path)

        self.group_menu.add_additional_keyboard(additional_keyboard)

    def send_menu(self, text_menu: str, parse_mode: str | None = None) -> MessageConfig:
        button_settings = []
        row = []

        if self.group_menu:
            button_settings.append(self.group_menu.settings)
            row.append(self.MENU_ROW)

        is_end = self.group_menu.is_end_page
        len_menu = self.group_menu.len_pages
        back_button = buttons.BACK_BUTTON if not self.group_menu.page == 0 and len_menu > 1 else ()
        next_button = buttons.NEXT_BUTTON if len_menu > 1 and not is_end else ()
        menu_buttons = buttons.MENU_BUTTONS if len_menu > 1 else ()

        if self.group_menu.additional_keyboard is not None and self.group_menu.page == 0:
            button_settings.append(self.group_menu.additional_keyboard)
            row.append(1)

        button_settings.append(menu_buttons + (ButtonSettings(self.group_menu.reset_path,
                                                              buttons.RESET_TEXT_GROUP_MENU),
                                               ButtonSettings(self.group_menu.back_path,
                                                              buttons.BACK_TEXT_GROUP_MENU)))
        row.append(self.MENU_BUTTONS_ROW)

        if next_button or back_button:
            button_settings.append(back_button + next_button)
            row.append(len(button_settings[-1]))

        configs = MessageConfig(button_settings=tuple(button_settings),
                                row_buttons=tuple(row),
                                text_message=text_menu,
                                parse_mode=parse_mode)

        return configs

    def exit_menu(self):
        if self.group_menu:
            self.group_menu.clear()

    def browsing(self, event: str, text: str, parse_mode: str) -> MessageConfig:
        if event == 'back':
            self.group_menu.back_page()
        elif event == 'next':
            self.group_menu.next_page()

        configs = self.send_menu(text_menu=text, parse_mode=parse_mode)

        return configs

    def reset_menu(self, reset_path: str, button_text: str, text: str) -> MessageConfig:
        self.group_menu.clear()
        return MessageConfig(text_message=text,
                             button_settings=(ButtonSettings(reset_path, button_text),),
                             row_buttons=1)

    @staticmethod
    def number_button(event: str) -> int:
        if '_' not in event:
            raise error_types.EventSintaxisError(event)
        return int(event.split('_')[1])

    def restore_menu_button(self, number_button: int) -> int:
        page = self.group_menu.page
        size = self.group_menu.size

        return page*size+number_button

    def menu_keyboard(self, global_state: str, state: str,
                      event: str, texts_buttons: tuple[str, ...]) -> tuple[ButtonSettings, ...]:
        size = self.group_menu.size
        button_setting = []
        for number, text in zip(range(len(texts_buttons)), texts_buttons):
            button_setting.append(ButtonSettings(
                CallBackData.creating_callback(global_state, state, f'{event}_{number % size}'), text))
        return tuple(button_setting)
