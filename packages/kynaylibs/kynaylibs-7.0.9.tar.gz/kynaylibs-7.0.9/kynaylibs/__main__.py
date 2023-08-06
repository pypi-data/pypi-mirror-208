import importlib
from asyncio import get_event_loop_policy
from platform import python_version as py

from modules import ALL_MODULES
from pyrogram import __version__ as pyro
from pyrogram import idle
from uvloop import install

from kynaylibs import *
from kynaylibs.nan import *
from kynaylibs.nan.utils.db import *

from .version import __version__ as nay

BOT_VER = "8.1.0"


MSG_ON = """
**Naya Premium Actived ✅**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
◉ **Versi** : `{}`
◉ **Phython** : `{}`
◉ **Pyrogram** : `{}`
◉ **Kynaylibs** : `{}`
**Ketik** `{}alive` **untuk Mengecheck Bot**
╼┅━━━━━━━━━━╍━━━━━━━━━━┅╾
"""


async def main():
    await app.start()
    LOGGER("Naya Premium").info("Memulai Naya-Pyro..")
    for all_module in ALL_MODULES:
        importlib.import_module(f"naya.modules.{all_module}")
    for bot in bots:
        try:
            await bot.start()
            ex = await bot.get_me()
            user_id = ex.id
            await ajg(bot)
            await buat_log(bot)
            botlog_chat_id = await get_botlog(user_id)
            try:
                await bot.send_message(
                    botlog_chat_id, MSG_ON.format(BOT_VER, py(), pyro, nay, CMD_HANDLER)
                )
            except BaseException as a:
                LOGGER("Info").warning(f"{a}")
            LOGGER("Info").info("Startup Completed")
            LOGGER("✓").info(f"Started as {ex.first_name} | {ex.id} ")
            ids.append(ex.id)
        except Exception as e:
            LOGGER("X").info(f"{e}")
    await idle()
    install()
    await aiosession.close()


if __name__ == "__main__":
    get_event_loop_policy().get_event_loop().run_until_complete(main())
