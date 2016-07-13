"""
   Quote recording extension.
   Records things people say. Does not say anything itself.
   Hooks: PRIVMSG
"""

import re
import time

import irc_message
import extension

# stop creating .pyc files
# sys.dont_write_bytecode = True

class QuoteRecorder(extension.Extension):
   name = "Quote Recorder"
   db = None

   def __init__(self, bot, db, record_isare=True):
      super(QuoteRecorder, self).__init__(bot)
      self.db = db
      self.record_isare = record_isare
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }


   def privmsg_handler(self, msg):
      sender = msg.getSender()
      message = msg.trail

      if ord(message[0]) == 1:
         # message[1:7] should be 'ACTION' and message[:-1] should be \1 as well
         # convert it into sender's name plus the rest of the message
         message = sender + message[7:-1]

      numquotes = self.db.quotes.count()
      newquote = {
         'author': sender,
         'quote': message,
         'tstamp': time.time(),
         'index': numquotes,
      }

      if self.record_isare:
         # see if this quote contains "is" or "are" so it can be marked specially
         isare = re.findall('([^\s]+)\s+(?:is|are)', message)
         if len(isare) > 0:
            new_isare = []
            for x in isare:
               # could insert a list of words that don't register here, like "this" or "they"
               new_isare.append(x.lower())
            newquote['is'] = new_isare

      self.db.quotes.insert(newquote)
      return False


   def cleanup(self):
      pass

