#! /usr/bin/python3

# From
# https://stackoverflow.com/questions/37499739/how-can-i-send-a-image-by-using-mosquitto
# 
# see workspace/chiliverde/send_image_via_mqtt.py for the other end of
# this transaction

import paho.mqtt.client as mqtt
MQTT_SERVER = "10.5.1.19"  # Mosquitto broker
MQTT_PATH = "Image"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    f = open('output.jpg', "wb")
    f.write(msg.payload)
    print("Image Received")
    f.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()

