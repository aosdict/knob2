"""
   Main module, demonstrates setting up and using a bot.
"""

import bot
import irc_message
import extension
import pymongo
from bson.objectid import ObjectId
import sys
import time
import random

import extensions.karma_tracker as karma_tracker

mclient = pymongo.MongoClient('localhost', 27017)
db = mclient['jbot']


'''
# Save a message from someone in the database so it can be retrieved later.
def save_quote(message, sender):
   if ord(message[0]) == 1:
      # message[1:7] should be 'ACTION' and message[:-1] should be \1 as well
      # convert it into sender's name plus the rest of the message
      message = sender + message[7:-1]

   numquotes = db.quotes.count()
   newquote = {
      'author': sender,
      'quote': message,
      'tstamp': time.time(),
      'index': numquotes,
   }

   # see if this quote contains "is" or "are" so it can be marked specially
   isare = re.findall('([^\s]+)\s+(?:is|are)', message)
   if len(isare) > 0:
      new_isare = []
      for x in isare:
         # could insert a list of words that don't register here, like "this" or "they"
         new_isare.append(x.lower())
      newquote['is'] = new_isare

   db.quotes.insert(newquote)


# Handle a command to the bot. Commands could be virtually anything.
# Returns True if the message should not be parsed after handling the command.
def handle_command(bot, message, sender, original_recipient):
   cmd_list = message.split()
   # cmd_list[0] is expected to be the bot's name
   if len(cmd_list) < 2:
      # can't really do anything without a command
      return False

   if cmd_list[1] == 'quote':
      # pick random number mod numquotes and get the quote with that index
      numquotes = db.quotes.count()
      quotenum = random.randint(0, numquotes-1)
      quote = db.quotes.find_one({'index': quotenum})
      recipient = sender if original_recipient == bot.nick else original_recipient
      bot.say('"' + quote['quote'] + '" -- ' + quote['author'], recipient)
      return True

   return False


# Hook for PRIVMSG commands and reacting to them. This will be the biggest part of most bots.
def privmsg_fn(bot, msg):
   sender = msg.getName()
   recipient = msg.params[0]
   message = msg.trail

   # look for a command to the bot (denoted by any string starting with the bot's nick)
   if message.find(bot.nick) == 0:
      if handle_command(bot, message, sender, recipient):
         return

   is_private = (recipient == bot.nick)

   if not is_private:
      # public message in a channel
      channel = recipient


      # add this message to the database of quotes for this sender
      save_quote(message, sender)
'''

settings = {
}

# handle command-line args
if len(sys.argv) != 4:
   print 'Usage:', sys.argv[0], 'server nick channel_list'
   sys.exit(1)

server = sys.argv[1]
start_nick = sys.argv[2]
channels = sys.argv[3].split(',')

jbot = bot.Bot(settings)

# initialize all extensions
karma_ext = karma_tracker.KarmaTracker(jbot, db)

# jbot.add_hook('PRIVMSG', privmsg_fn)

jbot.add_extension(karma_ext)

jbot.connect(server, start_nick)

for chan in channels:
   jbot.join('#'+chan)

jbot.interact()
