"""
   Bot module. Contains the Bot class and all functions necessary for
   setting up, starting, and running a bot.
"""

import sys
import socket
import select
import errno

import irc_message

# stop creating .pyc files
sys.dont_write_bytecode = True

class Bot:
   sock = None
   nick = ""
   settings = {}
   hooks = {}

   def __init__(self, settings = {}):
      self.sock = None
      self.settings = settings
      # TODO: make a setting for "notify level" controlling what gets printed
      # at different priority levels.

      # hooks is a dictionary mapping IRC command strings, 
      # like 'PRIVMSG', 'NICK' or '224', to functions that will be called with
      # this bot instance and an IRC object whenever the bot receives a message 
      # of that command.
      # By default it automatically responds to PING messages with pongs.
      self.hooks = {
         'PING': self._pong
      }
      # TODO: add hooks for successful channel join, nick (changes self.nick)


   # Send a string to the IRC server over the socket. This just removes the
   # boilerplate \r\n on everything.
   def __socksend(self, line):
      self.sock.send(line + '\r\n')

   # Get a line from the IRC server. Raises an EOFError if the connection is closed for some reason,
   # and also takes care of the \r\n on the end of every line.
   def __get_line(self):
      data = ''
      c = ''
      while c != '\n':
         c = self.sock.recv(1)
         data += c
      if not data:
         raise EOFError('Connection closed unexpectedly')

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
            print 'Connection error: Connection refused by server'
         elif serr.errno == errno.ENOEXEC:
            print variables.server,"connection error: Exec format error (maybe the server you specified doesn't exist, or you have a problem connecting to the Internet)"
         else:
            print variables.server,'connection error:',errno.errcode[serr.errno]
         raise serr

      attempt_nick = nick
      self.__socksend('USER %s %s %s :%s' % (ident, server, server, realname))
      self.__socksend('NICK %s' % attempt_nick)

      command = ""
      # wait for 001 (successful connection to the server)
      while command != "001":
         try:
            msg = irc_message.IrcMessage(self.__get_line())
         except EOFError as e:
            print 'Connection closed while waiting for 001'
            raise e
         except ValueError as e:
            print 'Problem parsing received line: %s' % e

         command = msg.command
         if command == '001':
            print 'Connection succeeded'
            self.nick = attempt_nick
         elif command == '433':
            print 'Nickname', attempt_nick, 'was already in use'
            attempt_nick += '_'
            print 'Trying with', attempt_nick
            self.__socksend('NICK ' + attempt_nick)
         else:
            print 'Unknown IRC command:', msg


   # Attempts to join a channel.
   # TODO: allow this to take a list of channels
   def join(self, channelName):
      if len(channelName) < 1:
         print 'Warning: tried to call join with an empty channel name, ignoring'
         return
      if channelName[0] != '#':
         self.__socksend('JOIN #'+channelName)
      else:
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
      if recipient == self.nick:
         print 'Warning: bot tried to send a message to itself'
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
               user_input = sys.stdin.readline().rstrip('\n')
               if user_input.lower() == 'quit':
                  return

            if sock == self.sock:
               try:
                  msg = irc_message.IrcMessage(self.__get_line())
                  print msg
               except EOFError:
                  print 'Connection closed unexpectedly'
                  return
               except ValueError as e:
                  print 'Problem parsing received line: %s' % e

               if msg.command in self.hooks:
                  self.hooks[msg.command](self, msg)
               else:
                  pass
                  # print 'No hook found'


   ### 
   ### Default hook functions
   ### These should all have 1 preceding underscore
   ### 

   # Send a PONG to the server.
   def _pong(self, bot, msg):
      self.sock.send('PONG :Pong')


