"""
   Main module, demonstrates setting up and using a bot.
"""

import pymongo
from bson.objectid import ObjectId
import sys
import random

import bot
import irc_message
import extension

import extensions.karma_tracker as karma_tracker
import extensions.quote_recorder as quote_recorder

mclient = pymongo.MongoClient('localhost', 27017)
db = mclient['jbot']

'''
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

'''

# handle command-line args
if len(sys.argv) != 4:
   print 'Usage:', sys.argv[0], 'server nick channel_list'
   sys.exit(1)

server = sys.argv[1]
start_nick = sys.argv[2]
channels = sys.argv[3].split(',')

settings = {
}

jbot = bot.Bot(settings)

# initialize all extensions
karma_ext = karma_tracker.KarmaTracker(jbot, db)
quote_ext = quote_recorder.QuoteRecorder(jbot, db, True)

# jbot.add_hook('PRIVMSG', privmsg_fn)

# Order of extensions is important!
jbot.set_extensions([
   karma_ext,
   quote_ext,
])

jbot.connect(server, start_nick)

for chan in channels:
   jbot.join('#'+chan)

jbot.interact()
