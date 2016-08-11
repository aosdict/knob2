"""
   Hype extension.
   Replies to the !hype command and messages matching [hH]+[yY]+[pP]+[eE]+!*
   with "HYPE"
"""

import re

import irc_message
import extension

class Hype(extension.Extension):
   name = "Hype"

   def __init__(self, bot, settings={}):
      super(Hype, self).__init__(bot)
      self.__init_settings(settings)
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }

   def __init_settings(self, settings):
      pass

   def privmsg_handler(self, msg):
      recipient = msg.params[0]
      # only works in channels
      if recipient[0] != '#':
         return False

      if msg.trail[:5] == '!hype':
         self.hype(recipient)
         return True

      elif re.match('([gG][eE][tT] +)?[hH]+[yY]+[pP]+[eE]+!*', msg.trail):
         self.hype(recipient)
         return True

   def hype(self, recipient):
      self.bot.say('HYPE', recipient)
