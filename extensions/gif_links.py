"""
   Gif links extension
   Replies to the !gif or !randomgif commands with gifs
   retrieved via the Giphy API.
"""

import requests
import json

import irc_message
import extension

class GifLinks(extension.Extension):
   name = "GIF Links"

   def __init__(self, bot, settings={}):
      super(GifLinks, self).__init__(bot)
      self.__init_settings(settings)
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }

   def __init_settings(self, settings):
      pass

   def privmsg_handler(self, msg):
      recipient = msg.params[0]
      if recipient == self.bot.nick:
         recipient = msg.getSender()

      if msg.trail.startswith('!gif') or msg.trail.startswith('!randomgif'):
         gif_url = self.get_gif_link(msg.trail)
         self.bot.say(gif_url, recipient)
         return True
      else:
         return False

   def get_gif_link(self, trail):
      params = trail.split()[1:]
      # interpret any arguments to the command as tags
      if len(params) == 0:
         tag_str = ''
      else:
         tag_str = '&tag=%s' % '+'.join(params)

      r = requests.get("http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&fmt=json" + tag_str)
      gif_url = json.loads(str(r.content, 'utf-8').replace('\\',''))['data']['image_original_url']
      return gif_url

   def cleanup(self):
      pass
