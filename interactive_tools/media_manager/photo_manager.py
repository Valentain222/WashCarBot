from aiogram import types
from aiogram.types import InputMediaPhoto, FSInputFile

from containers.msg_mgmt_containers import PhotoContainer
from constants import messages
from interactive_tools.text_messages.text_manager import TextManager

from setups.bot_setup import bot


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
