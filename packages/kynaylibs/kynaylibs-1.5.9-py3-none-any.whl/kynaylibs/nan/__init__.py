import sys

import pyrogram
from naya.config import CMD_HNDLR as cmd
from pyrogram import *
from pyrogram import Client, filters


def naya(command: str, prefixes: cmd):
    def wrapper(func):
        @Client.on_message(filters.command(command, prefixes) & filters.me)
        async def wrapped_func(client, message):
            await func(client, message)

        return wrapped_func

    return wrapper


def devs(command: str):
    def wrapper(func):
        @Client.on_message(
            filters.command(command, ".") & filters.user(DEVS) & ~filters.me
        )
        def wrapped_func(client, message):
            return func(client, message)

        return wrapped_func

    return wrapper
