"""
   Command handling extension.
   Responds to users commanding the bot.
   Commands can come in many forms and be many things.
   Hooks: PRIVMSG
"""

import random

import irc_message
import extension

# stop creating .pyc files
# sys.dont_write_bytecode = True

class CommandHandler(extension.Extension):
   name = "Command Handler"
   db = None

   def __init__(self, bot, db):
      super(CommandHandler, self).__init__(bot)
      self.db = db
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }
      self.commands = {
         'quote': self._random_quote,
      }

   def privmsg_handler(self, msg):
      # Starting with ! is one common form of commands.
      # Others include the string starting with the bot's nick.
      if msg.trail[0] == '!':
         # interpret as a command
         cmd_list = msg.trail.split()
         command = cmd_list[0][1:]

         if not command in self.commands:
            return True

         params = cmd_list[1:]
         self.commands[command](params)

         return False

      # not a command
      return True


   # Say a randomly chosen quote from the database.
   # Enclose in " and attribute to the original author.
   def _random_quote(self, params):
      # pick random number mod numquotes and get the quote with that index
      numquotes = self.db.quotes.count()
      quotenum = random.randint(0, numquotes-1)
      quote = self.db.quotes.find_one({'index': quotenum})
      recipient = sender if original_recipient == bot.nick else original_recipient
      bot.say('"' + quote['quote'] + '" -- ' + quote['author'], recipient)
