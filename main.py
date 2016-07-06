"""
   Main module, demonstrates setting up and using a bot.
"""

import bot
import irc_message

settings = {
}

def privmsg_fn(bot, msg):
   sender = msg.getName()
   recipient = msg.params[0]
   if recipient == bot.nick:
      bot.say(msg.trail, sender)
   else:
      bot.say(msg.trail, recipient)


jbot = bot.Bot(settings)
jbot.add_hook('PRIVMSG', privmsg_fn)
jbot.connect('irc.devel.redhat.com', 'hfuss')
jbot.join('#z')
jbot.interact()
