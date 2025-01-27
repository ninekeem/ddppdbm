import enum
from typing import Any, Type

from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.config import get_config

from src.yamlparser import Telegram


class PermissionLevel(enum.IntEnum):
    admin = 10
    moderator = 2
    user = 1
    denied = 0


class AuthFilter(BaseFilter):
    def __init__(self, minimum_level=PermissionLevel.user):
        self.level = minimum_level
        self.tc = Telegram(get_config())

    async def get_permission_level(self, user_id):
        user = self.tc.access.get(user_id)
        if user:
            return PermissionLevel[user['level']]

        return PermissionLevel.denied

    async def __call__(self, message: Message) -> bool:
        print(self.tc)
        user_perms = await self.get_permission_level(message.from_user.id)
        return user_perms >= self.level
