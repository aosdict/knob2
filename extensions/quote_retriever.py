"""
   Quote retrieving extension.
   Responds to the !quote command and spits out random quotes
   Hooks: PRIVMSG
"""

import random

import irc_message
import extension

# stop creating .pyc files
# sys.dont_write_bytecode = True

class QuoteRetriever(extension.Extension):
   name = "Quote Retriever"
   db = None

   def __init__(self, bot, db):
      super(QuoteRetriever, self).__init__(bot)
      self.db = db
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }


   def privmsg_handler(self, msg):
      recipient = msg.params[0]
      if recipient == self.bot.nick:
         recipient = msg.getSender()

      if msg.trail[:6] == '!quote':
         self._say_random_quote(recipient)
         return True

      return False


   # Say a randomly chosen quote from the database.
   # Enclose in " and attribute to the original author.
   def _say_random_quote(self, recipient):
      # pick random number mod numquotes and get the quote with that index
      numquotes = self.db.quotes.count()
      quotenum = random.randint(0, numquotes-1)
      quote = self.db.quotes.find_one({'index': quotenum})
      self.bot.say('"' + quote['quote'] + '" -- ' + quote['author'], recipient)


   def cleanup(self):
      pass
