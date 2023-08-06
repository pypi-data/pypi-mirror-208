# ᴀsᴋ-ᴘʏʀᴏ :->

> sᴛᴀʀᴛ ᴀsᴋ-ᴄʟɪᴇɴᴛ ᴡɪᴛʜ @ᴀᴘᴘ [ᴘʏʀᴏɢʀᴀᴍ ᴄʟɪᴇɴᴛ]
```python
  from askpyro import Askclient
  from pyrogram import Client ,filters
  
  app = Client("my_account")
  read = Askclient(app)

  @app.on_message(filters.command("start"))
  async def start_pm(c: app, m: Message):
    answer = await read.ask(m, text)
    if answer.text:
     print(answer.text)
    await answer.reply("ɪ ɢᴏᴛ ᴀɴsᴡᴇʀ..")

  app.run()
```


### ɪɴsᴛᴀʟʟɪɴɢ :->

```bash
pip3 install askpyro
```

<details>
<summary><h3>
- <b> ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ ɪɴ ᴘʏʀᴏɢʀᴀᴍ :-></b>
</h3></summary>
<a href="https://github.com/Abishnoi69/Askpyro/wiki/Conversation"><img src="https://img.shields.io/badge/ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ-903022f?logo=github"></a>
</details>

<details>
<summary><h3>
- <b> ᴡɪᴋɪ / ʜᴏᴡ ᴛᴏ ᴜsᴇ :-></b>
</h3></summary>
<a href="https://github.com/Abishnoi69/askpyro/wiki"><img src="https://img.shields.io/badge/ᴡɪᴋɪ-1589F0?logo=github"></a>
</details>

<details>
<summary><h3>
- <b> ᴇxᴀᴍᴘʟᴇ :-></b>
</h3></summary>
<a href="https://github.com/Abishnoi69/askpyro/tree/main/examples"><img src="https://img.shields.io/badge/ᴇxᴀᴍᴘʟᴇs-c5f015?logo=github"></a>
</details>

<details>
<summary><h3>
- <b> ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ :-></b>
</h3></summary>
<a href="https://telegram.me/AbishnoiMF"><img src="https://img.shields.io/badge/-Support%20Group-blue.svg?style=for-the-badge&logo=Telegram"></a>
</details>


━━━━━━━━━━━━━━━━━━━━
## ɴᴏᴛᴇ :->

- This library is made for my personal Project so don't take it deeply  [you can use this 24*7 running ] 
- My Project [AbgRobot](https://t.me/AbgRobot) & [Exon_Robot](https://t.me/Exon_Robot) 
- Enjoy Baby 

━━━━━━━━━━━━━━━━━━━━ 
 
<details>
<summary><h3>
- <b>ᴄʀᴇᴅɪᴛs :-></b>
</h3></summary>

➥ [𝐀𝖻𝗂𝗌𝗁𝗇𝗈𝗂] ↬ <a href="https://github.com/Abishnoi69" alt="Abishnoi69"> <img src="https://img.shields.io/badge/ᴀʙɪsʜɴᴏɪ-90302f?logo=github" /></a>  

➥ [𝐏ʏʀᴏɢʀᴀᴍ] ↬ <a href="https://github.com/pyrogram" alt="Pyrogram"> <img src="https://img.shields.io/badge/Pyrogram-90302f?logo=github" /></a>  
  
➥ [𝐒ᴘɪᴅᴇʀ] ↬ <a href="https://github.com/Surendra9123" alt="Surendra9123"> <img src="https://img.shields.io/badge/SPiDER-90302f?logo=github" /></a>  
━━━━━━━━━━━━━━━━━━━━
</details>
