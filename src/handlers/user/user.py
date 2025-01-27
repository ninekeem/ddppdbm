import logging

from aiogram.types import Message


async def start(message: Message) -> None:
    logging.info(msg=f'id: {str(message.from_user.id)}, first_name: {message.from_user.first_name} | {message.text}')
    await message.reply("This bot rules S-DDRace / DDPP SQLite3 Database.")