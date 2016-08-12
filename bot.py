"""
   Bot module. Contains the Bot class and all functions necessary for
   setting up, starting, and running a bot.
"""

import sys
import socket
import select
import errno
import traceback
import random

import irc_message
import extension

# stop creating .pyc files
sys.dont_write_bytecode = True

class Bot:
   sock = None
   nick = ""
   settings = {}
   hooks = {}
   extensions = []

   def __init__(self, settings = {}):
      self.sock = None
      self.__init_settings(settings)
      self.extensions = []
      # TODO: make a setting for "notify level" controlling what gets printed
      # at different priority levels.

      # hooks is a dictionary mapping IRC command strings, 
      # like 'PRIVMSG', 'NICK' or '224', to functions that will be called with
      # this bot instance and an IRC object whenever the bot receives a message 
      # of that command.
      # By default it automatically responds to PING messages with pongs.
      self.hooks = {
         'PING': self._pong,
      }
      # Separate set of system hooks that is only used before the 
      # connection is formally established.
      self.pre_welcome_hooks = {
         '432': self._try_reformatted_nick,
         '433': self._try_underscore_nick,
         'NOTICE': self._show_notice,
      }
      # TODO: add hooks for successful channel join, nick (changes self.nick)


   # Initialize the settings, to defaults if not given.
   def __init_settings(self, settings):
      self.show_say = settings.get('show_say', False)
      self.message_print_level = settings.get('message_print_level', 1)


   # Send a string to the IRC server over the socket. This just removes the
   # boilerplate \r\n on everything.
   def __socksend(self, line):
      self.sock.sendall((line + '\r\n').encode('utf-8'))


   # Get a line from the IRC server. Raises an EOFError if the connection is closed for some reason,
   # and also takes care of the \r\n on the end of every line.
   def __get_line(self):
      data = bytearray()
      c = ''
      while c != b'\n':
         c = self.sock.recv(1)
         data += c
      if not data:
         raise EOFError('Connection closed unexpectedly')

      data = str(data, 'utf-8')
      return data.rstrip('\r\n')


   # Open connection to an IRC server.
   # This has a while loop parsing commands, but it will exit 
   # once it is alerted to the connection message.
   # This isn't expected to be able to be on multiple servers at once.
   # May be called before or after setting hooks.
   def connect(self, server, nick, port=6667, ident="x", realname="x"):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
         self.sock.connect((server, port))
      except socket.error as serr:
         if serr.errno == errno.ECONNREFUSED:
            print('Connection error: Connection refused by server')
         elif serr.errno == errno.ENOEXEC:
            print(variables.server, "connection error: Exec format error (maybe the server you specified doesn't exist, or you have a problem connecting to the Internet)")
         else:
            print(variables.server,'connection error:',errno.errcode[serr.errno])
         raise serr

      self.__socksend('USER %s %s %s :%s' % (ident, server, server, realname))
      self.__socksend('NICK %s' % nick)

      command = ""
      # wait for 001 (successful connection to the server)
      while command != "001":
         try:
            line = self.__get_line()
            msg = irc_message.IrcMessage(line)
         except EOFError as e:
            print('Connection closed while waiting for 001')
            raise e
         except ValueError as e:
            print('Problem parsing received line: %s' % e)

         command = msg.command
         if command == '001':
            print('Connection succeeded')
            self.nick = msg.params[0]
         elif command in self.pre_welcome_hooks:
            self.pre_welcome_hooks[command](msg)
         else:
            print('Unknown IRC command:', msg)


   # Attempts to join a channel.
   # TODO: allow this to take a list of channels
   def join(self, channelName):
      if len(channelName) < 1:
         print('Warning: tried to call join with an empty channel name, ignoring')
         return
      if channelName[0] != '#':
         channelName = '#' + channelName
      self.__socksend('JOIN '+channelName)


   # Add a new hook. This assigns a function to a certain type of command.
   # Preferably, hooks should be added prior to connecting.
   def add_hook(self, command, fn):
      self.hooks[command] = fn


   # Make the bot say a message to a given channel or nick.
   def say(self, msg_str, recipient):
      # It should never try to send a direct message to itself.
      # This can cause a feedback loop where it keeps resending
      # messages which will eventually get it kicked for flooding.
      if self.show_say:
         print('Saying', msg_str, 'to', recipient)
      if recipient == self.nick:
         print('Warning: bot tried to send a message to itself')
         return
      self.__socksend('PRIVMSG %s :%s' % (recipient, msg_str))


   # Interacts with the IRC server. This will start a loop that will not exit until the bot is
   # terminated manually or the server closes the connection. Inside the loop, the bot will
   # read and interpret commands according to its hooks.
   def interact(self):
      while True:
         read_socks, write_socks, err_socks = select.select([sys.stdin, self.sock], [], [])

         for sock in read_socks:
            if sock == sys.stdin:
               user_input = sys.stdin.readline().rstrip('\n').split()
               cmd = user_input[0].lower()
               if cmd == 'quit':
                  self.__socksend('QUIT :' + ' '.join(user_input[1:]))
                  return

               elif cmd == 'tell':
                  if len(user_input) < 3:
                     print('Too few arguments to tell')
                  else:
                     self.say(' '.join(user_input[2:]), user_input[1])

               elif cmd == 'join':
                  if len(user_input) < 2:
                     print('Too few arguments to join')
                  else:
                     self.join(user_input[1])


            elif sock == self.sock:
               # first get and parse the message
               try:
                  msg = irc_message.IrcMessage(self.__get_line())
               except EOFError:
                  print('Connection closed unexpectedly')
                  return
               except ValueError as e:
                  print('Problem parsing received line: %s' % e)

               # then run it through the list of extensions
               halt = False
               handled = False
               for ext in self.extensions:
                  try:
                     retn = ext.act(msg)
                     if retn == True:
                        halt = True
                        handled = True
                        break
                     if retn == False:
                        handled = True
                     # if retn is anything else, set neither halt nor handled

                  except Exception as e:
                     print('Exception triggered from message:', msg)
                     print('in extension', ext.name)
                     print(e)
                     traceback.print_exc()

               # if no extension told it to terminate parsing, try
               # calling the hook for it if there is one.
               # This counts as handling and halting the message.
               # For this reason, the default hooks list should be kept minimal.
               if not halt:
                  if msg.command in self.hooks:
                     halt = True
                     handled = True
                     try:
                        self.hooks[msg.command](msg)
                     except Exception as e:
                        print('Exception triggered from message:', msg)
                        print('in hook', msg.command)
                        print(e)
                        traceback.print_exc()

               # based on halt and handle and message_print_level,
               # determine whether to print it
               if halt:
                  if self.message_print_level >= Bot.ALL_MESSAGES:
                     print('IRC message received (was handled and halted):')
                     msg.print()
               elif handled:
                  if self.message_print_level >= Bot.FALL_THROUGH_MESSAGES:
                     print('IRC message recieved (was handled but fell through):')
                     msg.print()
               else:
                  if self.message_print_level >= Bot.UNHANDLED_MESSAGES:
                     print('IRC message received (not caught by any extension or hook):')
                     msg.print()


   # The destructor for the bot. Closes connections and calls all
   # extensions' cleanup methods.
   def cleanup(self):
      self.sock.close()
      print('Connection closed successfully.')
      for ext in self.extensions:
         ext.cleanup()


   # Sets the bot's internal list of extensions.
   def set_extensions(self, extensions):
      self.extensions = extensions


   ### 
   ### Default hook functions
   ### These should all have 1 preceding underscore
   ### 

   # Null hook. Do not act on the message in any way.
   def _null_hook(self, msg):
      pass

   # Send a PONG to the server.
   def _pong(self, msg):
      self.__socksend('PONG :Pong')

   # Show a NOTICE sent by the server.
   def _show_notice(self, msg):
      print('NOTICE', msg.trail)

   # Take an erroneous nick returned by the server and attempt to
   # send a NICK that is the same, with all nonalphabetic characters removed.
   # If the returned nick is already alphabetic, try generating a 
   # random 8 lowercase letters nick.
   def _try_reformatted_nick(self, msg):
      # get the nick
      bad_nick = msg.params[1]
      # prevent case of _try_underscore_nick appending so many
      # underscores that it grows too long
      bad_nick = bad_nick.rstrip('_')
      if bad_nick.isalpha():
         attempt = ''
         for x in range(8):
            attempt += random.choice('abcdefghijklmnopqrstuvwxyz')
      else:
         attempt = ''.join([i for i in bad_nick if i.isalpha()])

      print('Bad nick', bad_nick)
      print('Trying', attempt)
      self.__socksend('NICK %s' % (attempt))

   # When the server returns a nickname because it is already in use,
   # append an underscore and send that nick.
   def _try_underscore_nick(self, msg):
      taken_nick = msg.params[1]
      attempt = taken_nick + '_'
      print('Nickname', taken_nick, 'already in use')
      print('Trying', attempt)
      self.__socksend('NICK %s' % (attempt))


   ###
   ### Constants for various settings
   ###

   # message_print_level
   NO_MESSAGES = 0
   UNHANDLED_MESSAGES = 1
   FALL_THROUGH_MESSAGES = 2
   ALL_MESSAGES = 3



