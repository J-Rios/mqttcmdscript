# mqttcmdscript

Python tool that parse a **cmdscript** text file provided by the user to automate and execute the specified MQTT client instructions to subscribe and publish messages to different MQTT Broker topics.

## Requirements

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 mqttcmdscript.py mycmdscript.txt
```

## CMDScripts

A **cmdscript** is a plain text file that uses a special language to specify command instructions to control the MQTT client.

The cmdscript uses special keywords to specify each operation, here is a list of supported commands:

```text
# Related to General Connection Configuration
CFG_CLIENT_ID X - Setup Client ID "X" for the MQTT Connection (if not set, "mqttcmdscript_UUID" is used as default).
CFG_CLEAN_SESSION YES/NO - Setup Clean Session as "YES" or "NO" for the MQTT connection (if not set, "YES" is used as default).
CFG_KEEPALIVE N - Setup Client connection keepalive message sent each "N" seconds (if not set, "60" is used as default).

# Related to Secure Connection
CFG_USER X Y - Setup Client Username "X" and Password "Y" for the MQTT connection.
CFG_USE_TLS YES/NO - Setup to use TLS as "YES" or "NO" for the MQTT connection.
CFG_TLS_CERT X Y - Setup path to the client certificate and key files to use when TLS connection is set.

# Related to Periodic interaction
CFG_PUB_EACH T N X "Y" - Publish a MQTT message each "T" seconds with QoS "N", to topic "X" and message content "Y".

# Related to Connection/disconnection
CONNECT X Y - Connect to MQTT Broker/Server "X" and port "Y" baudrate speed.
DISCONNECT - Disconnect from the MQTT Broker/Server.

# Related to Time
DELAY X - Wait for X seconds.
DELAY_MS X - Wait for X milli-seconds.
DELAY_H X - Wait for X hours.

# Related to Message send/reception
PUB N X "Y" - Publish a single MQTT message with QoS "N", to topic "X" and message content "Y".
SUB N X Y - Subscribe to topic "X" with QoS "N", and store received messages to log file "Y".
```

### CMDScripts Examples

A simple example of a cmdscript that connects to a Broker and log some topics to log files:

```text
# Setup Broker MQTT
CONNECT test.mosquitto.org 1883

# Subscribe to multiple topics and store received messages to same log file
SUB 0 my_topic_1 received_msgs.log
SUB 0 my_topic_2 received_msgs.log
SUB 0 my_topic_3 received_msgs.log

# Subscribe to another topic and store received messages to other log file
SUB 0 my_topic_4 other_file.log

# This script doesn't end until user kill the process (i.e. Ctrl+C)
```

A simple example of a cmdscript that connects to a Broker and publish some messages to different topics:

```text
# Setup Broker MQTT
CONNECT test.mosquitto.org 1883

# Publish messages to 3 different topics
PUB 0 my_topic_1 "topic 1 message 1"
PUB 0 my_topic_2 "topic 2 message 1"
PUB 0 my_topic_2 "topic 3 message 1"
DELAY 5
PUB 0 my_topic_1 "topic 1 message 2"
PUB 0 my_topic_2 "topic 2 message 2"
PUB 0 my_topic_3 "topic 3 message 2"

# Disconnect from the Broker
DISCONNECT
```

A simple example of a cmdscript that connects to a Broker, subscribe to a couple of topics and publish some messages, will be the following:

```text
# Setup Broker MQTT
CONNECT test.mosquitto.org 1883

# Setup Subscriptions
SUB 0 request_topic received_msgs.log
SUB 0 response_topic received_msgs.log

# Publish messages waiting 5 seconds between them
PUB 0 request_topic "hello"
DELAY 5
PUB 0 request_topic "my"
DELAY 5
PUB 0 request_topic "world"
DELAY 5

# Disconnect from the Broker
DISCONNECT
```
