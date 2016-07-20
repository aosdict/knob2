"""
   Extension for handling assorted obscure commands.
   Without something to suppress these commands, they will clutter
   up the terminal and make it annoying to parse. However, one might
   want to see some of the messages, so this extension allows some
   customization of these obscure messages.
   Hooks: A LOT OF THINGS (TODO)
"""

import irc_message
import extension

class SundryCommands(extension.Extension):
   name = "Sundry Commands"

   def __init__(self, bot, settings={}):
      super(SundryCommands, self).__init__(bot)
      self.__init_settings(settings)
      self.hooks = {
         '001': self.handle_001, # welcome
         '002': self.handle_002, # your host is
         '003': self.handle_003, # server creation time
         '004': self.handle_004, # server version and supported user/channel modes
         '005': self.handle_005, # server supported list
         '250': self.handle_250, # server connection stats
         '251': self.handle_251, # users online
         '252': self.handle_252, # operators online
         '253': self.handle_253, # unknown connections
         '254': self.handle_254, # channels formed
         '255': self.handle_255, # number of clients/servers
         '265': self.handle_265, # local users (NONSTANDARD)
         '266': self.handle_266, # global users (NONSTANDARD)
         '372': self.handle_372, # motd
         '375': self.handle_375, # start of motd
         '376': self.handle_376, # end of motd
         # '432': self.handle_432, # erroneous nickname
         # '433': self.handle_433, # nickname already in use
      }

   def __init_settings(self, settings):
      self.show_server_info = settings.get('show_server_info', False)
      self.show_server_stats = settings.get('show_server_stats', False)
      self.show_motd = settings.get('show_motd', False)

   # Unimplemented handlers have a single return False statement.

   def handle_001(self, msg):
      # shouldn't ever be encountered while connected
      if self.show_server_info:
         print('(welcome)', msg.trail)
      return True

   def handle_002(self, msg):
      if self.show_server_info:
         print('(server info)', msg.trail)
      return True

   def handle_003(self, msg):
      if self.show_server_info:
         print('(server info)', msg.trail)
      return True

   def handle_004(self, msg):
      if self.show_server_info:
         print('(server info) Server version:', msg.params[2])
         print('(server info) User modes:', msg.params[3])
         print('(server info) Channel modes:', msg.params[4])
         if len(msg.params) > 5:
            print('(server info) Channel modes requiring parameters:', msg.params[5])
         if len(msg.params) > 6:
            print('(server info) User modes requiring parameters:', msg.params[6])
         if len(msg.params) > 7:
            print('(server info) Server modes:', msg.params[7])
         if len(msg.params) > 8:
            print('(server info) Server modes requiring parameters', msg.params[8])
      return True

   def handle_005(self, msg):
      if self.show_server_info:
         for param in msg.params[1:]:
            print('(server info) Server supports:', param)
      return True

   def handle_250(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.trail)
      return True

   def handle_251(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.trail)
      return True

   def handle_252(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.params[1], 'operators online')
      return True

   def handle_253(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.params[1], 'unknown connections')
      return True

   def handle_254(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.params[1], 'channels')
      return True

   def handle_255(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.trail)
      return True

   def handle_265(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.trail)
      return True

   def handle_266(self, msg):
      if self.show_server_stats:
         print('(server stats)', msg.trail)
      return True

   def handle_372(self, msg):
      if self.show_motd:
         print(msg.trail)
      return True

   def handle_375(self, msg):
      if self.show_motd:
         print('Start of MOTD')
      return True

   def handle_376(self, msg):
      if self.show_motd:
         print('End of MOTD')
      return True

   def cleanup(self):
      pass
