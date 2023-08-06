import asyncio
import logging
import os
import sys
import time
from ast import parse
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, __version__, enums, filters
from pytgcalls import GroupCallFactory

from .config import *
from .logging import LOGGER

CMD_HNDLR = CMD_HNDLR
CMD_HELP = {}
ids = []


aiosession = ClientSession()
scheduler = AsyncIOScheduler()
StartTime = time.time()
START_TIME = datetime.now()


loop = asyncio.get_event_loop()


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="naya",
            api_hash=API_HASH,
            api_id=API_ID,
            bot_token=BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = self.me
        self.LOGGER(__name__).info(
            f"@{usr_bot_me.username} based on Pyrogram v{__version__} "
        )

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Naya-Pyro stopped. Bye.")


app = Bot()

if not BOT_TOKEN:
    LOGGER(__name__).error("WARNING: BOT TOKEN TIDAK DITEMUKAN, SHUTDOWN BOT")
    sys.exit()

bot1 = (
    Client(
        name="bot1",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION1,
        in_memory=False,
    )
    if SESSION1
    else None
)

bot2 = (
    Client(
        name="bot2",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION2,
        in_memory=False,
    )
    if SESSION2
    else None
)

bot3 = (
    Client(
        name="bot3",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION3,
        in_memory=False,
    )
    if SESSION3
    else None
)

bot4 = (
    Client(
        name="bot4",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION4,
        in_memory=False,
    )
    if SESSION4
    else None
)

bot5 = (
    Client(
        name="bot5",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION5,
        in_memory=False,
    )
    if SESSION5
    else None
)
bot6 = (
    Client(
        name="bot6",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION6,
        in_memory=False,
    )
    if SESSION6
    else None
)

bot7 = (
    Client(
        name="bot7",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION7,
        in_memory=False,
    )
    if SESSION7
    else None
)

bot8 = (
    Client(
        name="bot8",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION8,
        in_memory=False,
    )
    if SESSION8
    else None
)

bot9 = (
    Client(
        name="bot9",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION9,
        in_memory=False,
    )
    if SESSION9
    else None
)

bot10 = (
    Client(
        name="bot10",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION10,
        in_memory=False,
    )
    if SESSION10
    else None
)


bots = [
    bot for bot in [bot1, bot2, bot3, bot4, bot5, bot6, bot7, bot8, bot9, bot10] if bot
]

for bot in bots:
    if not hasattr(bot, "group_call"):
        setattr(bot, "group_call", GroupCallFactory(bot).get_group_call())
