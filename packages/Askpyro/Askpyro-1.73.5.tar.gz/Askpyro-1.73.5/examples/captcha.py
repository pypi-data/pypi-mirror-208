import random
from pyrogram import filters, Client
from askpuro import Askclient
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermission

app = Client("AskPyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

read = Askclient(app)



@app.on_message(filters.new_chat_members & filters.group)  
async def Captcha(c: app, m: Message):
 me = await c.get_me()
 await c.restrict_chat_member(m.chat.id, m.from_user.id, ChatPermissions(can_send_messages=False))
 await c.send_message(m.chat.id, "ɢᴏ ᴛᴏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴀɴᴅ sᴏʟᴠᴇ ᴄᴀᴘᴛᴄʜᴀ...!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴏ ᴘʀɪᴠᴀᴛᴇ..", url=f"http://t.me/{me.username}?start=captcha_{str(m.chat.id)}")]]))


@app.on_message(filters.command("start") & filters.private)  
async def CaptchaPM(c: app, m: Message):
 try:
  text = m.text[7:].split("_")
  chat_id = int(text[1])
 except:
  text = None
 if text and text[0] == "captcha":
  try:
    chat = await app.get_chat_member(chat_id, m.from_user.id)
  except Exception as a:
    await m.reply(a)
    return
  a = random.choice(range(10))
  b = random.choice(range(10))
  c = a + b
  ans = await read.ask(m, f"**ᴡʜᴀᴛ ɪs {a} + {b}?**")
  if ans.text == str(c):
    try:
      await c.restrict_chat_member(chat_id, m.from_user.id, ChatPermissions(can_send_messages=True))
    except Exception as a:
      await m.reply(a)
      return
    await ans.reply("sᴜᴄᴄᴇssғᴜʟ ᴀᴘᴘʀᴏᴠᴇᴅ ! ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀᴛ ɪɴ ɢʀᴏᴜᴘ ✔️")
  else:
    await ans.reply("ᴛʀʏ ᴀɢᴀɪɴ..!")
 else:
     #anything else
     pass
     
app.run()
