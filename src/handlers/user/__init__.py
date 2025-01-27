from aiogram import Router
from aiogram.filters import CommandStart

from . import user


def prepare_router() -> Router:
    user_router = Router(name='user')

    user_router.message.register(user.start, CommandStart())

    return user_router