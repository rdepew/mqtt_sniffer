import getopt
import sys
sys.path.insert(0, "./tahu/client_libraries/python/")

import paho.mqtt.client as mqtt
from sparkplug_b import *       # for decode_payload()

# Global variables
searchText = ""

# Decoding the Sparkplug B payload
def decode_payload(pl):
    payload = sparkplug_b_pb2.Payload()
    payload.ParseFromString(pl)
    print(payload)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("spBv1.0/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global searchText
    # print(msg.topic+" "+str(msg.payload))
    # print(msg.topic)
    if searchText != "" and searchText in msg.topic:
        print(msg.topic)
        tokens = msg.topic.split("/")
        if tokens[0] == "spBv1.0" and tokens[2] == "DDATA":
            decode_payload(msg.payload)
        else:
            print(msg.payload)
    else:
        print(msg.topic+" "+str(msg.payload))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection ****************************************")
        sys.exit(2)

# Process command-line parameters before running main program.

def usage():
    print('python3 %s <options>' % sys.argv[0])
    print('Options:')
    print('-h or --help                       : print this message')
    print('-i <ipaddr> or --brokerip <ipaddr> :  MQTT broker IP address')
    print('-s <text> or --search <text>       : search for text in topic')
    print('Search text is optional. If specified, output is filtered to ')
    print(' show only topics containing the search text.')
    print('This program assumes that username & password are not required.')
    print('If username and password are required, use mqtt_sniffer.py')
    print('instead.')

def parse_cmdline(argv):
    serverIp = "127.0.0.1"
    global searchText
    try:
        opts, args = getopt.getopt(argv,"hi:s:", 
            ["help", "brokerip=", "search="])
    except getopt.GetoptError:
        print("Error: Command line syntax error")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--search"):
            searchText = arg
        elif opt in ("-i", "--brokerip"):
            serverIp = arg
    return serverIp

# Main program

if __name__ == '__main__':
    serverIp = parse_cmdline(sys.argv[1:])
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    try:
        print("Connecting to ", serverIp)
        client.connect(serverIp, 1883, 60)
    except OSError:
        print('Error: MQTT broker %s is unreachable.' % serverIp)
        sys.exit(2)
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stopped", sys.argv[0], "gracefully")
