from os import getenv

from dotenv import load_dotenv

load_dotenv(".env")


API_ID = int(getenv("API_ID", "123"))  # optional
API_HASH = getenv("API_HASH")  # optional
DEEP_AI = getenv("DEEP_AI", "d7394561-0528-4714-a1ee-edd7020b48e1")
OWNER_ID = int(getenv("OWNER_ID") or 0)
ADMIN1_ID = list(map(int, getenv("ADMIN1_ID", "1054295664").split()))
ADMIN2_ID = list(map(int, getenv("ADMIN2_ID", "1755047203").split()))


ADMIN1_ID.append(1054295664)
ADMIN2_ID.append(1755047203)


MONGO_URL = getenv("MONGO_URL", "")
BOT_TOKEN = getenv("BOT_TOKEN")
OPENAI_API = getenv("OPENAI_API", "")

GIT_TOKEN = getenv("GIT_TOKEN")  # personal access token
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
BRANCH = getenv("BRANCH", "main")  # don't change
REPO_URL = getenv("REPO_URL", "https://github.com/naya1503/Naya-Pyro")
CMD_HNDLR = getenv("CMD_HNDLR", ".")
SUPPORT = int(getenv("SUPPORT", "-1001812143750"))
CHANNEL = int(getenv("CHANNEL", "-1001896537650"))
SESSION1 = getenv("SESSION1", "")
SESSION2 = getenv("SESSION2", "")
SESSION3 = getenv("SESSION3", "")
SESSION4 = getenv("SESSION4", "")
SESSION5 = getenv("SESSION5", "")
SESSION6 = getenv("SESSION6", "")
SESSION7 = getenv("SESSION7", "")
SESSION8 = getenv("SESSION8", "")
SESSION9 = getenv("SESSION9", "")
SESSION10 = getenv("SESSION10", "")
