###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from autobahn.twisted.resource import WebSocketResource



class PingServerProtocol(WebSocketServerProtocol):

   def doPing(self):
      if self.run:
         self.sendPing()
         self.factory.pingsSent[self.peer] += 1
         print("Ping sent to {} - {}".format(self.peer, self.factory.pingsSent[self.peer]))
         reactor.callLater(1, self.doPing)

   def onPong(self, payload):
      self.factory.pongsReceived[self.peer] += 1
      print("Pong received from {} - {}".format(self.peer, self.factory.pongsReceived[self.peer]))

   def onConnect(self, request):
      print("Client connecting: {}".format(request.peer))

   def onOpen(self):
      print("Connection open")
      self.factory.pingsSent[self.peer] = 0
      self.factory.pongsReceived[self.peer] = 0
      self.run = True
      self.doPing()

   def onClose(self, wasClean, code, reason):
      self.run = False
      print("Connection closed: wasClean = {}, code = {}, reason = {}".format(wasClean, code, reason))



class PingServerFactory(WebSocketServerFactory):

   def __init__(self, uri, debug):
      WebSocketServerFactory.__init__(self, uri, debug = debug)
      self.pingsSent = {}
      self.pongsReceived = {}



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory = PingServerFactory("ws://localhost:9000",
                               debug = 'debug' in sys.argv)

   factory.protocol = PingServerProtocol
   listenWS(factory)

   resource = WebSocketResource(factory)

   root = File(".")
   root.putChild("ws", resource)
   site = Site(root)

   reactor.listenTCP(8080, site)

   reactor.run()
