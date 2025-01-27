from aiogram import Router
from aiogram.filters import Command
from aiogram import F

from src.middlewares.DatabaseMiddleware import DatabaseMiddleware

from . import admin
from src.keyboards.UserPageKeyboard import PageCallbackFactory
from src.filters.AuthFilter import AuthFilter, PermissionLevel


def prepare_router() -> Router:
    admin_router = Router(name='admin')

    admin_router.message.filter(AuthFilter(minimum_level=PermissionLevel.moderator))
    admin_router.message.middleware(DatabaseMiddleware())

    admin_router.message.register(admin.help_message, Command("help"))
    admin_router.message.register(admin.chat, Command("chat"))
    admin_router.message.register(admin.get_user, Command("get_user"),)
    admin_router.message.register(admin.get_user_by_id,F.text.regexp(r"^\/user(\d+)$").as_("digits"))
    admin_router.message.register(admin.freeze, Command("freeze"))
    ###
    admin_router.message.register(admin.set_user, Command("set_user"), AuthFilter(minimum_level=PermissionLevel.admin))
    admin_router.message.register(admin.prem, Command("prem"), AuthFilter(minimum_level=PermissionLevel.admin))

    admin_router.callback_query.middleware(DatabaseMiddleware())
    admin_router.callback_query.register(admin.scroll_user_list_keyboard, PageCallbackFactory.filter())
    return admin_router