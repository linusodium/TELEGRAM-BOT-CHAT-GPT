import os

from dotenv import load_dotenv

load_dotenv()


SERVER_CRT = os.getenv("SERVER_CRT")
SERVER_KEY = os.getenv("SERVER_KEY")
OPEN_AI_KEY = os.getenv("API_KEY")
TG_BOT_TOKEN = os.getenv("TOKEN")
YOKASSA_KEY = os.getenv("YOKASSA_KEY")
YOKASSA_SHOP = os.getenv("YOKASSA_SHOP")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUB_MAIN_BOT_TOKEN = os.getenv("SUB_MAIN_BOT_TOKEN")
SUB_MAIN_IDS = os.getenv("SUB_MAIN_IDS")


