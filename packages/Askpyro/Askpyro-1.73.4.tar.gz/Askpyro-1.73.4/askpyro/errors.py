from pyrogram.types import ForceReply
import asyncio
import logging

class errors:
   class timeout:
     code,text,cancel,unknown,cb,basic = 101,None,False,False,False,False 
     timeout = error = "[100] Time Out ..!"
   class cancel:
     code,text,timeout,unknown,cb,basic = 102,None,False,False,False,False 
     cancel = error = "[102] Listening cancelled...!"
   class unknown:
     code,text,timeout,cancel,cb,basic = 103,None,False,False,False,False 
     error = unknown = "[103] Unknown Error...!"
   class cb:
     code,text,timeout,cancel,unknown,basic = 104,None,False,False,False,False 
     error = cb = "[104] Expected a callback query...!"
   class basic:
      error = basic = "Parameter type Invalid check again...!"
      code,text,timeout,cancel,cb,unknown = 105,None,False,False,False,False
         
