"""
   Echo extension.
   Simple extension that does nothing more than
   echo whatever someone says back at them.
"""

import irc_message
import extension


class Echo(extension.Extension):
   name = "Echo"

   def __init__(self, bot):
      super(Echo, self).__init__(bot)
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }


   # Handle PRIVMSG commands.
   def privmsg_handler(self, msg):
      sender = msg.getSender()
      recipient = msg.params[0]
      if recipient == self.bot.nick:
         # private message
         self.bot.say(msg.trail, sender)
      else:
         self.bot.say(msg.trail, recipient)

      return False
