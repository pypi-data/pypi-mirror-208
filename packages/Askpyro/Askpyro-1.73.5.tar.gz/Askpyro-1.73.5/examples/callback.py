from pyrogram import filters, Client
from pyrogram.types import CallbackQuery
from pyrocon import Askclient

app = Client("AskPyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

read = Askclient(app)

@app.on_callback_query()  
async def callback(_, msg: CallbackQuery):
    """https://github.com/Abishnoi69/Askpyro/wiki/callback"""
    answer = await read.ask(msg, "ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙʀᴏ ?", cb=True)
    await q.message.edit_text(f"ʏᴏᴜʀ ᴀɴsᴡᴇʀ ɪs {answer.text}")
    
app.run()
