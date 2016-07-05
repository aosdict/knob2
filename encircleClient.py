#!/usr/bin/env python

import sys
import encircleLib as elib
import socket
import select
import signal
import encircleSettings as settings
import encircleVars as variables
import time
import errno
import os # may be moved if read conf stuff gets moved

# Client globals
inputStr = ''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Send a raw string to the IRC server
def socksend(string):
   s.send(string+"\r\n")

# Get a single line from the IRC server
def getLine():
   tmp=s.recv(1)
   if not tmp: # connection closed
      return None

   while '\n' not in tmp:
      tmp += s.recv(1)

   tmp = tmp.rstrip('\r\n')
   return tmp

# Connect to IRC
def connect(port=6667):
   print 'Attempting to connect to', variables.server
   # set up socket things
   try:
      s.connect((variables.server, port))
   except socket.error as serr:
      if serr.errno == errno.ECONNREFUSED:
         print variables.server,'connection error: Connection refused'
      elif serr.errno == errno.ENOEXEC:
         print variables.server,"connection error: Exec format error (maybe the server you specified doesn't exist, or you have a problem connecting to the Internet)"
      else:
         print variables.server,'connection error:',errno.errcode[serr.errno]
      return False
   return True

# Formats a nickname
def fmtNick(nick):
   return "<"+nick+">"

# Cleans up and closes the program
def finish(mess="", code=0, quitmsg='Quit'):
   socksend('QUIT :'+quitmsg)
   s.close()
   if mess != "": print mess
   sys.exit(code)

# begin program execution
#
# ONLY CLASSES AND FUNCTIONS AND VARIABLES BEFORE THIS
#

# stop creating .pyc files
sys.dont_write_bytecode = True

# initial default values for stuff
# TODO: try without x and see what happens
attemptIdent = 'x'
attemptRealname = 'x'
attemptPassword = ''
attemptChannel = ''
attemptPort = 6667

# read prefs from ~/.irc_conf here


# usage: [name] server nick [[--channel=<channel>] [--port=<port>] [--realname=<realname>] [--ident=<ident>] [--password=<password>]]
if len(sys.argv) < 3:
   print 'Usage: encircle server nick [options]'
   print '  options: --channel= --realname= --ident= --password='
   print '           --raw-output'
   print '           --show-server-stats'
   print '           --show-motd'
   print '           --show-begins-and-ends'
   print '           --raw-commands'
   print '           --hide-pings'
   print '           --show-nonstandard'
   print '           --show-time'
   sys.exit(1)

variables.server = sys.argv[1]
attemptNick = sys.argv[2]

for x in range(3, len(sys.argv)):
   st = sys.argv[x]
   if st[:9] == '--channel':
      attemptChannel = st[10:]
   elif st[:6] == '--port':
      attemptPort = st[7:]
      if not attemptPort.isdigit():
         print '--port argument must be a number'
         sys.exit(1)
      attemptPort = int(attemptPort)
   elif st[:10] == '--realname':
      attemptRealname = st[11:]
   elif st[:7] == '--ident':
      attemptIdent = st[8:]
   elif st[:10] == '--password':
      attemptPassword = st[11:]
   elif st == '--raw-output':
      settings.formatOutput = False
   elif st == '--show-server-stats':
      settings.hideServerStats = False
   elif st == '--show-motd':
      settings.hideMOTD = False
   elif st == '--show-begins-and-ends':
      settings.hideBeginsEnds = False
   elif st == '--raw-commands':
      settings.formatCommands = False
   elif st == '--no-pings':
      settings.showPings = False
   elif st == '--show-nonstandard':
      settings.ignoreNonstandard = False
   elif st == '--show-time':
      settings.showTime = True
   else:
      print 'Unrecognized option '+st
      sys.exit(1)

# try to connect
sock = connect(attemptPort)
if sock == False:
   print "Failed to connect"
   sys.exit(1)

# send in user info
socksend("USER "+attemptIdent+" "+variables.server+" "+variables.server+" "+attemptRealname)
if attemptPassword != '': socksend("PASS "+attemptPassword)
socksend("NICK "+attemptNick)

# wait for a 001 success message from the server
while 1:
   line = getLine()

   if line is None:
      finish("Could not finish connecting to the server.", 1)

   results = elib.parse(line)
   if results.command == "001":
      # hooray, success!
      print 'Connection succeeded'
      variables.currNick = results.params[0]
      break
   if results.command == "433":
      # nickname in use, generate a random temporary nickname
      print 'Nickname', attemptNick, 'was already in use.'
      attemptNick += '_'
      socksend('NICK '+attemptNick)
      continue

if attemptChannel != '': socksend('JOIN '+attemptChannel)

while True:
   try:
       data = getLine()
   except socket.error as serr:
      if serr.errno == errno.ECONNRESET:
         finish("Connection closed.", 1, 'Connection closed')
      raise serr

   if data is None:
      finish('Connection terminated', 1, 'Connection terminated')

   elif data[:4] == "PING":
      socksend('PONG :Pong')
      if settings.showPings:
         print 'PING'
      continue

   elif data[:5] == 'ERROR':
      # something very bad is happening
      print data

   else:
      elib.process(data)


