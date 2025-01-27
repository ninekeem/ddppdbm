import logging
from contextlib import suppress
from re import Match

import aiosqlite
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text

from src.db.user import User, UserIsLoggedIn, PlayerNotFound
from src.filters.AuthFilter import AuthFilter, PermissionLevel
from src.keyboards.UserPageKeyboard import get_keyboard_fab, PageCallbackFactory
from src.utils.format import format_user, columns, format_users

record_limit = 50
async def help_message(message: Message) -> None:
    text = Text("""
/get_user column value
/user<id>
/set_user username column value
/freeze <username>
/prem <username> <days>
    """)
    await message.answer(text=text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2)


async def chat(message: Message) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')
    await message.reply(
        f'If you can see this message, you have access\nchat_id: {message.chat.id}\nthread_id: {message.message_thread_id}')

async def get_user_by_id(message: Message, digits: Match[str], db: aiosqlite.Connection) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')
    user_id = digits.group(1)
    result = await User.get(db, **{"ID": str(user_id)})
    print(result[0])
    hide_sensitive = await AuthFilter().get_permission_level(message.from_user.id) < PermissionLevel.admin
    answer = format_user(columns, result[0], hide_sensitive) if result[0] else "No user found"
    await message.reply(answer)

user_data = {}


async def get_user(message: Message, command: CommandObject, db: aiosqlite.Connection) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')

    args = command.args.split() if command.args else []

    if len(args) < 2: await message.reply("usage: /get_user column value"); return
    param_names = [x.lower() for x in args[::2]]
    param_values = args[1::2]
    if not set(param_names).issubset(set(x.lower() for x in columns)):
        await message.reply(f"Provided: {param_names}\nAllowed:{columns}")
        return
    params = dict(zip(param_names, param_values))

    result = await User.get(db, **params, limit=record_limit)
    from_user_id = message.from_user.id
    
    user_data[from_user_id] = {
        "params": params,
        "offset": 0,
    }

    match len(result):
        case 0:
            await message.reply("No users found")
        case 1:
            hide_sensitive = await AuthFilter().get_permission_level(message.from_user.id) < PermissionLevel.admin
            answer = format_user(columns, result[0], hide_sensitive) if result[0] else "No user found"
            await message.reply(answer)
        case _ if len(result) > 1:
            answer = f"""Users 0-{record_limit}:\n{format_users(result)}"""

            await message.reply(answer, reply_markup=get_keyboard_fab())

async def update_user_list_fab(message: Message, new_value: int, db: aiosqlite.Connection) -> None:
    with suppress(TelegramBadRequest):
        from_user_id = message.chat.id
        user_data[from_user_id]['offset'] = new_value
        user_params = user_data[from_user_id]['params']
        print("user_params", user_params)
        result =  await User.get(db, **user_params, limit=record_limit, offset=new_value)
        answer = f"""Users {new_value}-{new_value+record_limit}:\n{format_users(result)}"""
        await message.edit_text(answer, reply_markup=get_keyboard_fab())

async def scroll_user_list_keyboard(callback: types.CallbackQuery, db: aiosqlite.Connection, callback_data: PageCallbackFactory) -> None:
    user_value = user_data.get(callback.from_user.id, 0)
    if callback_data.action == "change":
        user_data[callback.from_user.id]['offset'] = user_value['offset'] + callback_data.value
        logging.info(user_data[callback.from_user.id]['offset'])
        await update_user_list_fab(callback.message, user_data[callback.from_user.id]['offset'], db)

    await callback.answer()

async def set_user(message: Message, command: CommandObject, db: aiosqlite.Connection) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')
    args = command.args.split() if command.args else []
    if len(args) < 3: await message.reply("usage: /set_user nickname column value"); return
    param_names = args[1::2] # skip nickname
    param_values = args[2::2]

    params = dict(zip(param_names, param_values))
    print(param_names, param_values)
    print(params)
    try:
        await User.set(db, username=args[0], **params)
    except Exception as e:
        await message.reply("Something went wrong. Error: {}".format(e))


async def prem(message: Message, command: CommandObject, db:aiosqlite.Connection) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')

    args = command.args.split() if command.args else []
    if len(args) != 2: await message.reply("usage: /prem username 30"); return
    username = args[0]
    days = args[1]
    try:
        await User.set_premium(db, username, days)
    except UserIsLoggedIn:
        await message.reply("Noo! Player is logged in!")
    except PlayerNotFound:
        await message.reply("Player not found?")
    else:
        await message.reply("Player modified")


async def freeze(message: Message, command: CommandObject, db:aiosqlite.Connection) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')
    args = command.args.split() if command.args else []
    if len(args) != 2: await message.reply("usage: /freeze username 1"); return
    username = args[0]
    status = args[1]
    try:
        await User.set_freeze(db, username, status)
    except UserIsLoggedIn:
        await message.reply("Noo! Player is logged in!")
    except PlayerNotFound:
        await message.reply("Player not found?")
    else:
        await message.reply("Player modified")

