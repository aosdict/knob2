"""
   Main module, demonstrates setting up and using a bot.
"""

import bot
import irc_message
import pymongo
import sys
import re

mclient = pymongo.MongoClient('localhost', 27017)
db = mclient['jbot']

def privmsg_fn(bot, msg):
   sender = msg.getName()
   recipient = msg.params[0]
   message = msg.trail

   if recipient == bot.nick:
      # private message
      recipient = sender
   else:
      # public message in a channel

      # look for a ++ or -- in the string (karma up/down)
      karma_mod_list = re.findall('[^ ]+[+-][+-]', message)

         
      # add this message to the database of quotes for this sender

   bot.say(msg.trail, recipient)

settings = {
}


jbot = bot.Bot(settings)
jbot.add_hook('PRIVMSG', privmsg_fn)
jbot.connect('irc.freenode.net', 'sjdhfkj')
jbot.join('#zszszs')
jbot.interact()
