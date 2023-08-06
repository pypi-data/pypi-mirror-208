from pyrogram import filters, Client
from pyrogram.types import Message
from askpyro import Askclient

app = Client("AskPyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

read = Askclient(app)

@app.on_message(filters.command("start"))  
"""https://github.com/Abishnoi69/askpyro/wiki/pyrogram-filters"""
async def filters_(c: app, m: Message):
    answer = await read.ask(m, "ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙʀᴏ ?", filter=(filters.text & filters.group))
    print(answer.text)

app.run()


