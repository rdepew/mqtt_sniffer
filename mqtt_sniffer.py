# File mqtt_sniffer.py
#
# Author: Ray Depew
# Created: 20211129

from binascii import a2b_base64
import datetime
import getopt
from socket import gethostname
import sys
from time import sleep

import paho.mqtt.client as mqtt

sys.path.insert(0, "./tahu/client_libraries/python/")
import sparkplug_b as sparkplug
from sparkplug_b import *

##### Constants and global variables #####

MQ_GROUPID = gethostname()
MQ_NODENAME = "listener"
MQ_DEVICE = "test"
save_img = False

MQ_DATATYPES = [
    "Unknown", "Int8", "Int16", "Int32", "Int64", "UInt8", "UInt16", 
    "UInt32", "UInt64", "Float", "Double", "Boolean", "String", 
    "DateTime", "Text", "UUID", "DataSet", "Bytes", "File", "Template"
    ]

file_byte_string = ""


##### MQTT Functions #####

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

def on_disconnect(client, userdata, rc):
    """Called when the client is unexpectedly disconnected."""
    if rc != 0:
        print("Unexpected disconnection ***********************************")
        sys.exit(2)

alias_nextServer = 0
alias_rebirth = 1
alias_reboot = 2

def on_message(client, userdata, msg):
    if nodename == "":
        print("%s %s" % (datetime.datetime.now(), msg.topic))
    tokens = msg.topic.split("/")
    if (tokens[0] == "spBv1.0" and tokens[1] == MQ_GROUPID
            and (tokens[2] == "NCMD" or tokens[2] == "DCMD")
            and tokens[3] == MQ_NODENAME):
        print("NCMD or DCMD received")
        inboundPayload = sparkplug_b_pb2.Payload()
        inboundPayload.ParseFromString(msg.payload)
        # print("Payload:", inboundPayload)
        for metric in inboundPayload.metrics:
            if (metric.name == "Node Control/Next Server" 
                    or metric.alias == alias_nextServer):
                print("'Node Control/Next Server' is not implemented",
                    " in this app.")
            elif (metric.name == "Node Control/Rebirth" 
                    or metric.alias == alias_rebirth):
                publishBirth()
            elif (metric.name == "Node Control/Reboot" 
                    or metric.alias == alias_reboot):
                publishBirth()
            else:
                print("Unknown command: " + metric.name)
    elif tokens[3] == nodename:
        print("%s %s" % (datetime.datetime.now(), msg.topic))
        if tokens[0] == "spBv1.0":
            if tokens[2] == "DDATA":
                decode_payload(msg.payload, nodename)
            elif tokens[2] == "DCMD":
                decode_dcmd(msg.payload, nodename)
            elif tokens[2] == "NCMD":
                decode_ncmd(msg.payload, nodename)
            # added 9/24/20
            elif tokens[2] == "DBIRTH":
                decode_payload(msg.payload, nodename)
            elif tokens[2] == "NBIRTH":
                decode_payload(msg.payload, nodename)
        else:
            print("Payload:", msg.payload)
    else:
        return

def publishBirth(client):
    publishNodeBirth(client)
    publishDeviceBirth(client)

def publishNodeBirth(client):
    print("Publishing Node Birth")
    # Create the node birth payload
    payload = sparkplug.getNodeBirthPayload()
    # Set up the Node Controls
    addMetric(payload, "Node Control/Next Server", alias_nextServer, 
            MetricDataType.Boolean, False)
    addMetric(payload, "Node Control/Rebirth", alias_rebirth, 
            MetricDataType.Boolean, False)
    addMetric(payload, "Node Control/Reboot", alias_reboot,
            MetricDataType.Boolean, False)
    # Publish the node birth certificate
    byteArray = bytearray(payload.SerializeToString())
    client.publish("spBv1.0/" + MQ_GROUPID + "/NBIRTH/" + MQ_NODENAME,
            byteArray, 0, False)

def publishDeviceBirth(client):
    print("Publishing Device Birth")
    # Get the payload
    payload = sparkplug.getDeviceBirthPayload()
    # Publish the initial data with the Device BIRTH certificate
    totalByteArray = bytearray(payload.SerializeToString())
    client.publish("spBv1.0/" + MQ_GROUPID + "/DBIRTH/" + MQ_NODENAME + "/" + 
        MQ_DEVICE, totalByteArray, 0, False)

def setup_mqtt(serverIp, username, password):
    global deathPayload
    global MQ_GROUPID
    global MQ_NODENAME
    global MQ_DEVICE
    print("In setup_mqtt()")
    # Set up the MQTT client connection
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    mqttClient.on_disconnect = on_disconnect
    mqttClient.on_message = on_message
    mqttClient.username_pw_set(username, password)
    # Create the node death payload
    deathPayload = sparkplug.getNodeDeathPayload()
    deathByteArray = bytearray(deathPayload.SerializeToString())
    mqttClient.will_set("spBv1.0/" + MQ_GROUPID + "/NDEATH/" + MQ_NODENAME, 
            deathByteArray, 0, False)
    try:
        mqttClient.connect(serverIp, 1883, 60)
    except OSError:
        print('Error: MQTT broker %s is unreachable.' % serverIp)
        sys.exit(2)
    # Short delay to allow connect callback to occur
    sleep(.1)
    mqttClient.loop()
    # Publish the birth certificates
    publishBirth(mqttClient)
    return mqttClient
    print("MQTT client is connected to broker %s" % serverIp)

def publishDData(mqttClient):
    # Publishing data takes four steps:
    # 1. payload = sparkplug.getDdataPayload() - two D's, as in DDATA
    # 2. addMetric(payload, ....)              - defined in sparkplug_b.py
    #    Repeat 2 as often as necessary, to build up a payload.
    # 3. byteArray = bytearray(payload.SerializeToString()) 
    #                                          - from sparkplug_b_pb2.py
    # 4. mqttClient.publish()                  - from paho.mqtt.client

    print("In publishDData(), but I don't know why")
    payload = sparkplug.getDdataPayload()
    addMetric(payload, "pi", 3, MetricDataType.UInt16, 31416)
    print("Publishing DDATA")
    byteArray = bytearray(payload.SerializeToString())
    mqttClient.publish("spBv1.0/" + MQ_GROUPID + "/DDATA/" + MQ_NODENAME
            + "/" + MQ_DEVICE, byteArray, 0, False)
    print(byteArray)

##### Other functions #####

def decode_payload(pl, nodename):
    global file_byte_string
    try:
        payload = sparkplug_b_pb2.Payload()
        payload.ParseFromString(pl)
    except:
        print("Could not parse DDATA payload from", nodename)
        print("Moving right along ...")
        file_byte_string=""
        return
    print(payload)
    for metric in payload.metrics:
        z = metric.string_value
        if metric.name == "camera_image/file":
            filename = metric.metadata.file_name
            content = metric.string_value
            size = metric.metadata.size
            seq = metric.metadata.seq
            # print("Rec'd chunk", seq, ",", size, "chars")
            if len(content) == 0 or size == 0:
                # Combine strings and save file.
                file_bytes = a2b_base64(file_byte_string)
                with open(filename, 'wb') as fl:
                    fl.write(file_bytes)
                print("Saved the binary file ", filename)
                # Zero out the string.
                file_byte_string = ""
            else:
                file_byte_string += content


def decode_dcmd(pl, nodename):
    dcmdPayload = sparkplug_b_pb2.Payload()
    dcmdPayload.ParseFromString(pl)
    print("********** DCMD for %s:\n%s" % (nodename, dcmdPayload))

def decode_ncmd(pl, nodename):
    ncmdPayload = sparkplug_b_pb2.Payload()
    ncmdPayload.ParseFromString(pl)
    print("********** NCMD for %s:\n%s" % (nodename, ncmdPayload))


##### Main part of program #####

def usage():
    print('python3 mqtt_sniffer.py <options>')
    print('Options:')
    print('-h or --help                       : print this message')
    print('-i <ipaddr> or --brokerip <ipaddr> : specify MQTT broker IP address')
    print('-n <name> or --brokername <name>   : specify MQTT broker name')
    print('-u <username> or --user <username> : specify username')
    print('-p <password> or --pass <password> : specify password')
    print('-N <nodename> or --node <nodename> : specify nodename')
    print('--saveimages                       : save image files (optional)')
    print('')
    print('You MUST specify one of brokerip or brokername, but not both')
    print('Username, password are optional')
    print('Nodename is optional, but recommended.')
    print('If nodename is specified, the program only reports DDATA')
    print('  messages from that node.')

def parse_cmdline(argv):
    serverIp = "52.13.116.147"
    serverName = "public.mqtthq.com"
    username = "test"
    password = "test"
    nodename = ""
    # print("Args are:", argv)
    try:
        opts, args = getopt.getopt(argv,"hi:n:u:p:N:", 
            ["help", "brokerip=", "brokername=", 
             "user=", "pass=", "node=", "saveimages"])
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
        elif opt in ("-n", "--brokername"):
            serverName = arg
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-p", "--pass"):
            password = arg
        elif opt in ("-N", "--node"):
            nodename = arg
        elif opt in ("--saveimages"):
            save_img = True
    return serverIp, serverName, username, password, nodename

if __name__ == '__main__':
    serverIp, serverName, \
            username, password, nodename = parse_cmdline(sys.argv[1:])
    mqttClient = setup_mqtt(serverIp, username, password)
    try:
        while(True):
            for _ in range(10):
                sleep(.1)
                mqttClient.loop()
    except KeyboardInterrupt:
        print("\nStopped", sys.argv[0], "gracefully")

