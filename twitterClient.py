'''
Twitter Client
'''
import asyncio
import getopt
import socket
import sys
import websockets

BUFFERSIZE = 1024

@asyncio.coroutine
def web_socket_client(message):
    '''
    Web sock client to send message and accept response
    '''
    websocket = yield from websockets.connect("ws://localhost:3002/")
    try:
        yield from websocket.send(message.encode())
        print("Sent: " + message)
        reply = yield from websocket.recv()
        reply = reply.decode()
    finally:
        yield from websocket.close()
    return "Got: " + reply

def build_client(server_type):
    '''
    Build a client appropriate for the server interface
    '''
    if server_type == "--websocket":
        return web_socket_client
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 3002))
    return client

def send_message(client, message):
    '''
    Send a message to the server and get it's response
    '''
    if isinstance(client, socket.socket):
        print("sending:", message, "Encoded:", message.encode())
        if not client.sendall(message.encode()) is None:
            print("Error in sendall of:" + message)
            print("Sent: " + message)
        print("waiting for reply")
        packet = client.recv(BUFFERSIZE).decode()
        print("Got: " + packet)
        client.close()
    else:
        print(asyncio.get_event_loop().run_until_complete(web_socket_client(message)))

def main():
    '''
    Client main
    '''
    server_type = ""
    help_string = "python3 TwitterClient.py [--websocket]\n"
    opts, args = getopt.getopt(sys.argv[1:], "", ["websocket"])
    for option in opts:
        if option[0] == "--websocket":
            server_type = option[0]
        else:
            print("Option error: " + option[0] + ", " + option[1])
            print(help_string)
            sys.exit(-1)
    send_message(build_client(server_type), " ")
    send_message(build_client(server_type), "RealSexyCyborg")
    send_message(build_client(server_type), "getEmbeddedStatus 1293170215153307660")

if __name__ == "__main__":
    main()
