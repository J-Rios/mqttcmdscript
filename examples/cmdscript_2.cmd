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