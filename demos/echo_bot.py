"""
   Echo bot demo, a simple bot that echoes whatever people say
   on channels or private messages.
"""

import bot
import irc_message

def privmsg_fn(bot, msg):
   sender = msg.getName()
   recipient = msg.params[0]
   if recipient == bot.nick:
      bot.say(msg.trail, sender)
   else:
      bot.say(msg.trail, recipient)

settings = {
}

jbot = bot.Bot(settings)
jbot.add_hook('PRIVMSG', privmsg_fn)
jbot.connect('irc.freenode.net', 'sjdhfkj')
jbot.join('#zszszs')
jbot.interact()
