from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, Message

from . import app
from askpyro.helpers import ikb, ikb2 


async def gen_button_kb(q: Message or CallbackQuery):
    return ikb(
        [
            [
                ("ɪɴʟɪɴᴇ 1", "buttons.back"),
            ],
            [("ɪɴʟɪɴᴇ 2", "Callback.2")],
        ],
    )


async def gen_button_kb2(m):
    return ikb2(
        [
            [
                ("ɪɴʟɪɴᴇ 1", "Callback1"),
                ("ɪɴʟɪɴᴇ 2", "Callback2"),
            ],
            [("ɪɴʟɪɴᴇ 3", "Callback3")],
        ],
        True,
        "back_callback",
    )


@app.on_message(filters.command("buttons"))
async def buttonkb_(c: app, m: Message):
    await m.reply_text(
        f"ᴇᴀsʏ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴ ᴜsɪɴɢ ᴀsᴋ-ᴘʏʀᴏ",
        reply_markup=(await gen_button_kb(m)),
    )
    return
  
  
@app.on_callback_query(filters.regex("^buttons."))
async def buttonkb_CB(c: app, q: CallbackQuery):
    data = q.data.split(".")[1]
    if data == "back":
        try:
            await q.message.edit_text(
                text=f"ᴇᴀsʏ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴ ᴜsɪɴɢ ᴀsᴋ-ᴘʏʀᴏ ",
                reply_markup=(await gen_button_kb(q.message)),
            )
        except MessageNotModified:
            pass
        await q.answer()
        return
