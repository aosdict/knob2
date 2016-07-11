"""
   Karma tracking extension.
   Records when users say "something++" or "something--" and uses a
   Mongo database to record their "karma" numbers.
"""

import re

import irc_message
import extension

# stop creating .pyc files
# sys.dont_write_bytecode = True

class KarmaTracker(extension.Extension):
   name = "Karma Tracker"
   db = None

   def __init__(self, bot, db):
      super(KarmaTracker, self).__init__(bot)
      self.db = db
      self.hooks = {
         'PRIVMSG': self.privmsg_handler
      }


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
   def _adjust_karma(self, karma_mod_list, channel, sender):
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
            print 'Warning: karma_mod_list encountered a name not followed by ++ or --:', s
            continue

         nick = s.rstrip('+-')
         user = self._get_user(nick)
         new_karma = user['karma'] + delta
         self.db.users.update({'nick': nick}, { '$set':  { 'karma': new_karma } })
         points_plural = "" if (new_karma == 1 or new_karma == -1) else "s"
         out_str = '%s now has %s point%s of karma' % (nick, new_karma, points_plural)
         print out_str
         self.bot.say(out_str, channel)


   def privmsg_handler(self, msg):
      karma_mod_list = re.findall('[^ ]+(?:\+\+|--)', msg.trail)
      if len(karma_mod_list) > 0:
         recipient = msg.params[0]
         sender = msg.getSender()
         self._adjust_karma(karma_mod_list, recipient, sender)
         return False
      else:
         return True

