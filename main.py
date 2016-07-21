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
import extensions.sundry_commands as sundry_commands

mclient = pymongo.MongoClient('localhost', 27017)
db = mclient['jbot']

# handle command-line args
if len(sys.argv) != 4:
   print('Usage:', sys.argv[0], 'server nick channel_list')
   sys.exit(1)

server = sys.argv[1]
start_nick = sys.argv[2]
channels = sys.argv[3].split(',')

# any settings for the bot
settings = {
   'show_say': True,
   'message_print_level': bot.Bot.UNHANDLED_MESSAGES,
}

# initialize bot
jbot = bot.Bot(settings)

# initialize all extensions
karma_ext_settings = {
   'prevent_spam': True,
   'karma_timeout': 5,
   'flush_period': 1,
   'print_karma_changes': False,
}
karma_ext = karma_tracker.KarmaTracker(jbot, db, karma_ext_settings)
quote_ext = quote_recorder.QuoteRecorder(jbot, db, True)
sc_ext_settings = {
   'show_server_stats': False,
   'show_server_info': False,
   'show_motd': False,
}
sc_ext = sundry_commands.SundryCommands(jbot, sc_ext_settings)

# Order of extensions is important!
jbot.set_extensions([
   karma_ext,
   quote_ext,
   sc_ext,
])

# connect to the given server with the given nick
jbot.connect(server, start_nick)

# join the specified channels
for chan in channels:
   jbot.join('#'+chan)

# start interacting with the server
jbot.interact()

# once the bot is killed by the user or server,
# call its cleanup procedures and its extensions'
jbot.cleanup()
