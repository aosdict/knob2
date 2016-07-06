"""
   Bot module. Contains the Bot class and all functions necessary for
   setting up, starting, and running a bot.
"""

import sys
import socket
import select
import errno

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
      # hooks is a dictionary mapping IRC command strings, 
      # like 'PRIVMSG', 'NICK' or '224', to functions that will be called with
      # a IRC object whenever a message of that command is received.
      self.hooks = {}


   # Send a string to the IRC server over the socket. This just removes the
   # boilerplate \r\n on everything.
   def __socksend(line):
      self.sock.send(line + '\r\n')

   def __get_line():
      data = self.sock.recv(1024)
      if not data:
         raise EOFError('Connection closed unexpectedly')
      


   # Open connection to an IRC server.
   # This isn't expected to be able to be on multiple servers at once.
   # May be called before or after setting hooks.
   def connect(self, server, nick, port=6667, ident="x", realname="x", channels=[]):
      self.nick = nick
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
      try:
         s.connect((server, port))
      except socket.error as serr:
         if serr.errno == errno.ECONNREFUSED:
            print 'Connection error: Connection refused by server'
         elif serr.errno == errno.ENOEXEC:
            print variables.server,"connection error: Exec format error (maybe the server you specified doesn't exist, or you have a problem connecting to the Internet)"
         else:
            print variables.server,'connection error:',errno.errcode[serr.errno]
         raise serr

      self.__socksend('USER %s %s %s :%s' % (ident, server, server, realname))
      self.__socksend('NICK %s' % nick)

