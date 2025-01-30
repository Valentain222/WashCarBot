from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from setups.bot_setup import bot
from containers.bot_containers import MessageConfig, ButtonSettings


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
