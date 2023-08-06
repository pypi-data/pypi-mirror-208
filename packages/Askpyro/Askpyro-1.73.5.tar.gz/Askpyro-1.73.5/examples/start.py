from pyrogram import filters, Client
from pyrogram.types import Message
from askpyro import Askclient

app = Client("AskPyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

read = Askclient(app)

@app.on_message(filters.command("start"))  
async def start_(c: app, m: Message):
    answer = await read.ask(m,"ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙʀᴏ ?")
    await answer.reply(f"ʏᴏᴜʀ ᴀɴsᴡᴇʀ ɪs {ans.text}")

    
asu.start()
