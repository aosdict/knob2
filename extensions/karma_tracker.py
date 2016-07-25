"""
   Karma tracking extension.
   Records when users say "something++" or "something--" and uses a
   Mongo database to record their "karma" numbers.
   Hooks: PRIVMSG
"""

import re
import threading
import time
from bson.objectid import ObjectId

import irc_message
import extension

# stop creating .pyc files
# sys.dont_write_bytecode = True

class KarmaTracker(extension.Extension):
   name = "Karma Tracker"
   db = None

   def __init__(self, bot, db, settings={}):
      super(KarmaTracker, self).__init__(bot)
      self.db = db
      self.__init_settings(settings)
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }
      if self.prevent_spam:
         # maintain a dictionary of tuples of (sender, karmaed) to timestamp
         # to prevent people from spamming karma
         self.recent_karma = {}
         self.exiting = False
         self.recent_karma_lock = threading.Lock()
         # start checking for recent karma expired
         threading.Thread(None, self.__recent_karma_expired).start()


   # Initialize the extension's settings based on what was passed to the constructor.
   def __init_settings(self, settings):
      self.allow_minus = settings.get('allow_minus', True)
      self.prevent_spam = settings.get('prevent_spam', True)
      self.karma_timeout = settings.get('karma_timeout', 300)
      # The flush_period should be significantly less than the karma_timeout, maybe only a few seconds.
      self.flush_period = settings.get('flush_period', 30)
      self.print_karma_changes = settings.get('print_karma_changes', False)


   # Run an infinite loop that checks every so often to flush out the recent_karma list.
   # This should be run in a new thread.
   def __recent_karma_expired(self):
      while not self.exiting:
         now = time.time()
         with self.recent_karma_lock:
            for key in self.recent_karma.copy():
               if now - self.recent_karma[key] > self.karma_timeout:
                  self.recent_karma.pop(key)

         time.sleep(self.flush_period)

      self.print("Karma Tracker polling thread finished")


   # Given a nick, return a dictionary representing the associated user in the database.
   # This will create a user if no user with the nick exists.
   def _get_user(self, nick):
      user = self.db.users.find_one({'nick': nick})
      if user is None:
         new_user = {
            'nick': nick,
            'karma': 0,
         }
         new_id = self.db.users.insert(new_user)
         user = self.db.users.find_one({'_id': ObjectId(new_id)})
      return user


   # Given a list of nicks with ++ or -- after them, adjust each user's karma accordingly.
   def _adjust_karma(self, karma_mod_list, sender, channel):
      for s in karma_mod_list:
         # don't let people change their own karma
         if s.find(sender) == 0:
            continue

         has_plusplus = ( s.find('++') >= 0 )
         has_minusminus = ( s.find('--') >= 0 )

         if has_plusplus and has_minusminus:
            # string has both ++ and -- in it, someone is probably trying to confuse the bot
            if len(karma_mod_list) == 1:
               self.bot.say("Don't try to break me.", channel)
               return
            # if there are other karma mods, go to them
            continue

         elif has_plusplus:
            delta = 1
         elif has_minusminus:
            delta = -1
         else:
            # neither ++ or -- happened, this should not be possible
            self.print('Warning: karma_mod_list encountered a name not followed by ++ or --:', s)
            continue

         nick = s.rstrip('+-')
         if self.prevent_spam:
            with self.recent_karma_lock:
               if (sender, nick) in self.recent_karma:
                  continue

         user = self._get_user(nick)

         new_karma = user['karma'] + delta
         self.db.users.update({'nick': nick}, { '$set':  { 'karma': new_karma } })
         if self.prevent_spam:
            with self.recent_karma_lock:
               self.recent_karma[(sender, nick)] = time.time()

         if self.print_karma_changes:
            incdecstr = "in" if delta == 1 else "de"
            self.print('Karma of %s %scremented by %s to %s' % (nick, incdecstr, sender, new_karma))

         out_str = '%s now has %s point%s of karma' % (nick, new_karma, self.plural(new_karma))
         self.bot.say(out_str, channel)


   def handle_karma_command(self, message, sender, channel):
      # Get and say the karma of the first param, and ignore anything else.
      try:
         nick = message.split()[1]
      except IndexError:
         nick = sender

      cursor = self.db.users.find_one({'nick': nick}, {'karma': 1, '_id': 0})
      try:
         karma = cursor['karma']
      except TypeError:
         out_str = '%s has never received karma' % nick
      else:
         out_str = '%s has %s point%s of karma' % (nick, karma, self.plural(karma))

      self.bot.say(out_str, channel)


   def privmsg_handler(self, msg):
      recipient = msg.params[0]
      sender = msg.getSender()

      # look for !karma or !points first
      if msg.trail[:6] == '!karma' or msg.trail[:7] == '!points':
         self.handle_karma_command(msg.trail, sender, recipient)
         return True

      if self.allow_minus:
         karma_mod_list = re.findall('[^ ]+(?:\+\+|--)', msg.trail)
      else:
         karma_mod_list = re.findall('[^ ]+\+\+', msg.trail)

      if len(karma_mod_list) > 0:
         self._adjust_karma(karma_mod_list, sender, recipient)
         return True
      else:
         return False

   def cleanup(self):
      self.print('Waiting for Karma Tracker thread to close...')
      self.exiting = True


   # Given a karma number, return 's' if the karma is plural
   # or '' if singular.
   def plural(self, karma):
      if karma == 1 or karma == -1:
         return ''
      else:
         return 's'
