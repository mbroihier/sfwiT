'''
Twitter Server - accepts websock requests, retrieves information from API
'''
import asyncio
import getopt
import json
import re
import socketserver
import sys
import websockets
from SFWIT import SFWIT

TWITTER = None

def getEmbeddedStatus(packet):
    returnInfo = TWITTER.getEmbeddedStatus(packet.split(" ")[1])
    return returnInfo

def getFollowing(packet):
    global TWITTER
    if TWITTER is None:
        TWITTER = SFWIT()
    returnInfo = TWITTER.getFollowing()
    following = json.loads(returnInfo)
    for screenName in following:
        COMMAND_LOOKUP[screenName] = getUserTimeline
    return returnInfo

def getUserTimeline(packet):
    global TWITTER
    returnInfo = TWITTER.getUserTimeline(packet)
    return returnInfo

COMMAND_LOOKUP = {
    "" : getFollowing,
    "getEmbeddedStatus" : getEmbeddedStatus}

BUFFERSIZE = 1024

def parse_command(packet):
    '''
    parse the incoming command - if null
    '''
    reply = ""
    command = packet.split(" ")[0]
    print("command:", command)
    if command in COMMAND_LOOKUP:
        print("Doing", command)
        reply = COMMAND_LOOKUP[command](packet)
    else:
        print("error:", COMMAND_LOOKUP.keys())

    if reply == "":
        return "Nak: illegal command - " + packet

    return reply

class Handler(socketserver.BaseRequestHandler):
    '''
    Handler Class for Twitter server requests
    '''

    def handle(self):
        '''
        Accept and process request
        '''
        print("packet received from client")
        packet = self.request.recv(BUFFERSIZE).strip().decode()
        print("got packet", packet)
        reply = parse_command(packet)
        print("got reply", reply)
        self.request.sendall(bytes(reply, "utf-8"))

    def finish(self):
        '''
        finish process request
        '''
        print("connection closing")


class TwitterServer(object):
    '''
    Twitter  server class
    '''
    @asyncio.coroutine
    def websocket_handler(self, websocket, path):
        '''
        Handler when running in websocket mode
        '''
        packet = yield from websocket.recv()
        packet = packet.strip().decode()
        reply = parse_command(packet)
        yield from websocket.send(bytes(reply, "utf-8"))

    def __init__(self, host, port, server_type):
        '''
        Constructor for NMI class
        '''
        if server_type == "--websocket":
            print("Starting websocket server.....")
            start_server = websockets.serve(self.websocket_handler, host, port)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        else:
            print("Starting TCP server.....")
            socketserver.TCPServer((host, port), Handler).serve_forever()

def main():
    '''
    Server main
    '''
    help_string = "python3 twitterServer.py [--websocket]"
    server_type = "" #default to TCP server
    opts, args = getopt.getopt(sys.argv[1:], "", ["websocket"])
    for option in opts:
        if option[0] == "--websocket":
            server_type = option[0]
        else:
            print("Option error: " + option[0] + ", " + option[1])
            print(help_string)
            sys.exit(-1)
    try:
        TwitterServer("localhost", 3002, server_type)
    except KeyboardInterrupt:
        print("Exiting Twitter Server gracefully")

if __name__ == "__main__":
    main()
