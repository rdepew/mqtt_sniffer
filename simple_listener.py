import paho.mqtt.client as mqtt
import getopt
import sys

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Failed to connect with result code " + str(rc))
        sys.exit(2)
    else:
        print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("spBv1.0/#", 0)
    client.subscribe("spAv1.0/#", 0)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    print(msg.topic)

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
    print('This program assumes that username & password are not required.')
    print('If username and password are required, use mqtt_listener.py')
    print('instead.')

def parse_cmdline(argv):
    serverIp = "127.0.0.1"
    try:
        opts, args = getopt.getopt(argv,"hi:", 
            ["help", "brokerip="])
    except getopt.GetoptError:
        print("Error: Command line syntax error")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        # TODO: Do an nslookup on both brokerip and brokername.
        # Exit with error if not found.
        # If serverName is given, convert to serverIp.
        # The rest of the program uses only serverIp.
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
