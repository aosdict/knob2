"""
   IRCMessage module. Bundles IRC data into a format that's easy to program
   with.
"""

import sys

# stop creating .pyc files
sys.dont_write_bytecode = True

class IrcMessage:
   prefix = ""
   command = ""
   params = []
   trail = ""

   # Constructor takes a line verbatim from an IRC server, which is then parsed
   # into the correct components. 
   def __init__(self, line):
      # IRC lines are broken into [:<prefix>] <command> [ <param> ... ] :<trail>

      # get prefix
      if line[0] == ':':
         prefixStart = 1
         prefixEnd = line.find(" ")
         if prefixEnd == -1:
            raise ValueError('Could not find end of prefix in line ' + line)
      else:
         prefixStart = 0
         prefixEnd = 0
      self.prefix = line[prefixStart:prefixEnd]

      # get trail, which is unique in that it is the first part of the line
      # to begin with " :"
      trailStart = line.find(" :")
      if trailStart >= 0:
         commandEnd = trailStart
         trailStart += 2
      else:
         commandEnd = len(line)
         trailStart = len(line)
      self.trail = line[trailStart:]

      # command and params are between the prefix and trail
      commandStart = prefixEnd+1 if prefixEnd > 0 else 0
      commandList = line[commandStart:commandEnd].split();
      if len(commandList) < 1:
         raise ValueError('Could not find a command in line ' + line)
      self.command = commandList[0]
      self.params = commandList[1:]


   # String conversion
   def __str__(self):
      string_form = 'PREFIX: "%s" COMMAND: "%s" PARAMS: "%s" TRAIL: "%s"'
      return string_form % (self.prefix, self.command, " ".join(self.params), self.trail)


   # If the prefix is user!~server.com or similar, gets "user" from it
   def getSender(self):
      return self.prefix.split('!')[0]


