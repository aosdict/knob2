"""
   Hype extension.
   Replies to the !hype command and messages matching [hH]+[yY]+[pP]+[eE]+!*
   with "HYPE"
"""

import re
import random

import irc_message
import extension

class Hype(extension.Extension):
   name = "Hype"
   hype_msgs = {
      'HYPE': 20,
      'HYPE HYPE HYPE': 5,
      'GET HYPE': 15,
      'hype': 2,
   }
   hype_msgs_total = 0
   for choice in hype_msgs:
      hype_msgs_total += hype_msgs[choice]

   exclamation_mark_prob = 0.3

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

   def _get_random_hype_msg(self):
      rand = random.uniform(0, Hype.hype_msgs_total)
      curr = 0
      for choice, weight in Hype.hype_msgs.items():
         if curr + weight >= rand:
            return choice
         curr += weight

   def hype(self, recipient):
      hype_msg = self._get_random_hype_msg()
      exclamation_str = ''
      if random.random() < Hype.exclamation_mark_prob:
         exclamation_str = '!' * random.randint(1,5)
      self.bot.say('%s%s' % (hype_msg, exclamation_str), recipient)

   def cleanup(self):
      pass
