"""
   Extension module. Abstract base class for any extensions that
   a programmer wants to register.
"""

# import abc
import sys

import irc_message

# stop creating .pyc files
sys.dont_write_bytecode = True

class Extension(object):

   # variables
   name = "" # expected to be supplied by the implementor
   hooks = {}
   bot = None


   def __init__(self, bot):
      self.bot = bot


   # Act on an irc message. This should not be called by the programmer.
   # Return a truth value representing whether the bot should continue
   # trying to call act on other messages.
   def act(self, msg):
      if msg.command not in self.hooks:
         return False

      return self.hooks[msg.command](msg)


   # Print a message to console. The message will be automatically
   # prefaced by the extension name to indicate where it's coming from.
   # Acts like normal print, with a variable number of args.
   def print(*args):
      self = args[0]
      ext_name_str = "(" + type(self).name + ")"
      args = ( ext_name_str, ) + args[1:]
      print(*args)
