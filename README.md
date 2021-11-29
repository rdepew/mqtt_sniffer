# mqtt_sniffer

MQTT Sniffer

Subscribes to a broker and snoops on incoming data.

The MQTT Sniffer runs on Python 3. Although it was developed on and for
small Linux systems, it will run on any Linux system. It should also be
compatible with Mac or Windows systems.

Windows users will not be able to run the installation script. They will
have to manually install the following Python 3 libraries:

- protobuf
- paho-mqtt


## To install the program the easy way:

If on a Zum, copy mqtt_sniffer.tar.gz to the directory `/home/devuser/apps` .

If not on a Zum, copy it to wherever you want to run it from.

Unpack the tarball using this command: `tar xzvf mqtt_sniffer.tar.gz` 

Change to the directory `mqtt_sniffer` .

Run the script `install-mqtt_sniffer.sh` and follow the on-screen prompts.


## To install the program the harder way:

If on a Zum, change to the directory `/home/devuser/apps` .

If not on a Zum, change to the directory you want to run the program from.

Clone the repo:
```
git clone https://github.com/rdepew/mqtt_sniffer.git
```

Either:
- Run the script `install-mqtt_sniffer.sh` and follow the on-screen prompts.

Or:
- Install the dependencies by executing these three commands:
```
sudo apt update -y
sudo apt install -y python3-pip python3-protobuf
pip3 install paho-mqtt
```


## To run the program:

Run it as
```
python3 mqtt_sniffer.py -i <broker-ip-address>
```

That only shows you the topic names. That may be all you need to see.

If you want to see all the data in a topic, then add the ‘-N’ option:
```
python3 mqtt_sniffer.py -i <broker-ip-address> -N <nodename>
```

The nodename is the first field after the DDATA keyword in a DDATA 
message.

There’s also a ‘-h’ or ‘--help' option if you need it.


### Real-life examples:

```
python3 mqtt_sniffer.py -i 45.33.105.244
python3 mqtt_sniffer.py -i 45.33.105.244 -N Z9-PE2_3732
```


## Other useful programs in the repo `mqtt_sniffer`:

* `simple_listener.py` - listens to everything that goes into the broker.
* `listener_and_decoder.py` - same as `simple_listener.py`, but it 
  decodes any SparkPlug B DDATA payloads.
  If a "search string" is specified, filters output to report only
  MQTT topics which contain the search string. For example:
  `python3 listener_and_decoder.py --search dogs` reports only topics
  with `dogs` in the topic namespace.
* `recv_image_via_mqtt.py` - a snippet of code that saves a binary file sent
  using plain vanilla MQTT, not Sparkplug B.

## What's this 'tahu' directory?

The 'tahu' directory has a small number of files copied from the Eclipse Tahu
project (see https://github.com/eclipse/tahu). I don't need everything in the
tahu repository, only the protobufs definitions and the Python files. Thanks
to the great project team at Eclipse Tahu.
