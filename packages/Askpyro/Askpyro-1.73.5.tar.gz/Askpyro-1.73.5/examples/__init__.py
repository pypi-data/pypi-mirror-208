from pyrogram import Client
from pyrocon import Askclient

app = Client("AskPyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

read = Askclient(app)
