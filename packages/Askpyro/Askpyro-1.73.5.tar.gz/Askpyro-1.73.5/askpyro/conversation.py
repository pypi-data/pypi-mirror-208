from pyrogram.types import ForceReply,Message,CallbackQuery
import asyncio
import logging
from .errors import errors
from pyrogram import Client,filters
from pyrogram.filters import Filter

class Askclient():
  def __init__(self,
               client : Client,
               clear : bool = True,
               timeout : int = 40,
               stop_cmd : str = "/cancel",
               placeholder : str = "Send required information...",
               msg_limit : int = 100
               ):
      if not isinstance(client, Client):
          print("Parameter client must be pyrogram Client object")
          return errors.basic
      if not isinstance(timeout, int):
          print("Parameter timeout must be Integer")
          return errors.basic
      if not isinstance(stop_cmd, str):
          print("Parameter stop_cmd must be str")
          return errors.basic
      if not isinstance(placeholder, str):
          print("Parameter placeholder must be str")
          return errors.basic
      if not isinstance(clear, bool):
          print("Parameter clear must be Boolean (True or False)")
          return errors.basic
      self.client : Client = client
      self.timeout : int = timeout
      self.stop_cmd : str = stop_cmd
      self.placeholder : str = placeholder
      self.msg_limit : int = msg_limit
      self.delete_msg : bool = clear

  async def ask(self,
                msg : Message or CallbackQuery,
                text : str,
                cb : bool = False,
                filter : Filter = False
                ):
     if not isinstance(cb,bool):
        print("Parameter cb must be Boolean (True or False)")
        return errors.basic
     if (cb and (not isinstance(msg,CallbackQuery))) or ((not cb) and (not isinstance(msg,Message))):
        if cb:
         print("Parameter msg must be CallbackQuery object")
         return errors.basic
        else:
         print("Parameter msg must be Message object")
         return errors.basic      
     if not isinstance(text,str):
        print("Parameter text must be str")
        return errors.basic
     if not (isinstance(filter,bool) or isinstance(filter,Filter)):
        print("Parameter filter must be pyrogram filters object")
        return errors.basic
     try:
         try:
             if msg.from_user:
                 anonymous = False
                 user_id = msg.from_user.id
             else:
                 anonymous = True
                 user_id = msg.sender_chat.id
         except Exception as e:
             logging.info(e)
             user_id = None
         if user_id:
             if cb:
                 uv = await self.client.send_message(chat_id=msg.message.chat.id,
                                                     text=text,
                                                     reply_markup=ForceReply(
                                                                             selective = True,
                                                                             placeholder = self.placeholder
                                                                            )
                                                     )
             else:
                 uv = await msg.reply(text = text,
                                         reply_to_message_id = msg.id,
                                         reply_markup=ForceReply(selective = True,
                                                                 placeholder = self.placeholder
                                                                 )
                                         )
             ans = await asyncio.wait_for(Askclient.wait(self, uv, anonymous, user_id, filter),
                                          timeout=self.timeout
                                          )
         else:
             return errors.unknown
     except Exception as e:
      logging.info("Time Out!")
      ans = errors.timeout
     try:
      if self.delete_msg:
        await uv.delete()
     except:
      pass
     return ans


  async def wait(self,uv,anonymous,user_id,filter):
      while True:
          try:
              ids = [uv.id + x for x in range(self.msg_limit)]
              ids.pop(0)
              for ans in (await self.client.get_messages(uv.chat.id, ids)):
                  ans.error = errors.unknown
                  try:
                      if anonymous:
                          user_id2 = ans.sender_chat.id
                      else:
                          user_id2 = ans.from_user.id
                  except:
                      user_id2 = "Nonne"
                  if filter:
                      is_user = True
                  else:
                      is_user = True if (user_id2 == user_id) else False
                  if ans and (not ans.empty) and (ans.text == self.stop_cmd) and is_user:
                      ans = errors.cancel
                      break
                  if ans and (not ans.empty) and is_user:
                      if filter:
                          fil = await filter(self.client, ans)
                      else:
                          fil = await filters.text(self.client, ans)
                      if fil:
                          ans.error = ans.cancel = ans.timeout = ans.anon = ans.unknown = False
                          break
              if (not ans.error) or (ans == errors.cancel):
                  break
          except Exception as e:
              logging.info(e)
              break
      return ans
