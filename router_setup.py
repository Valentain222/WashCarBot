from aiogram.filters.command import Command

from my_bot import MYBot

from aiogram import Router, types

from users_manager import Users

from containers import CallBackData

router = Router()
users = Users()


def structuring_callback(callback: str) -> CallBackData:
    structural_callback = CallBackData()
    structural_callback.callback_division(callback)

    return structural_callback


def callback_handler_data(callback: types.CallbackQuery) -> tuple[CallBackData, MYBot]:
    struct_callback = structuring_callback(callback.data)
    user = users.locate_user(callback.from_user.id)

    return struct_callback, user


@router.message(Command('restore', 'reset'))
async def restore(message: types.Message):
    user = users.locate_user(message.from_user.id)
    await user.state_command(message)


@router.message(Command('start'))
async def start(message: types.Message):
    user = users.locate_user(message.from_user.id)
    await user.start(message)


@router.callback_query(lambda callback: callback.data.startswith('interaction'))
async def interaction_handler(callback: types.CallbackQuery):
    struct_callback, user = callback_handler_data(callback)
    await user.parallel_actions(struct_callback)
    await user.interaction_entry_point(struct_callback)


@router.callback_query(lambda callback: callback.data.startswith('basic'))
async def basic_callback_query(callback: types.CallbackQuery):
    struct_callback, user = callback_handler_data(callback)
    await user.parallel_actions(struct_callback)
    await user.basic_callback_center(struct_callback)


@router.callback_query(lambda callback: callback.data.startswith('menu_operation'))
async def menu_handler(callback: types.CallbackQuery):
    struct_callback, user = callback_handler_data(callback)
    await user.menu_operations(struct_callback)


@router.message()
async def message_handler(message: types.Message):
    user = users.locate_user(message.from_user.id)
    await user.user_input(message)
