"""
   IRCMessage module. Bundles IRC data into a format that's easy to program
   with.
"""

class IrcMessage:
   prefix = ""
   command = ""
   params = []
   trail = ""

   # Constructor takes a line verbatim from an IRC server, which is then parsed
   # into the correct components. 
   def __init__(self, irc_line):
      # IRC lines are broken into [:]<prefix> <command> [ <param> ... ] :<trail>
    
      # get prefix
      prefixStart = 1 if (line[0] == ":") else 0
      prefixEnd = line.find(" ")
      self.prefix = line[prefixStart:prefixEnd]

      # get trail, which is unique in that it is the first part of the line
      # to begin with " :"
      trailStart = line.find(" :")
      if trailStart > 0:
         commandEnd = trailStart
         trailStart += 2
      else:
         commandEnd = len(line)
         trailStart = len(line)
      self.trail = line[trailStart:]

      # command and params are between the prefix and trail
      commandStart = prefixEnd+1
      commandString = line[commandStart:commandEnd].split();
      self.command = commandString[0]
      self.params = commandString[1:]
      

    # If the prefix is user!~server.com or similar, gets "user" from it
    def getName(self):
        return extractName(self.prefix)
