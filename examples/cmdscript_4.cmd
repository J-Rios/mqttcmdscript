# Setup Broker MQTT
CONNECT test.mosquitto.org 1883

# Publish message each 10 seconds
CFG_PUB_EACH 10 0 my_topic_1 "Hello World"

# Publish message each minute
CFG_PUB_EACH 60 0 my_topic_2 "Hello World"

# Subscribe to multiple topics and store received messages to same log file
SUB 0 my_topic_1 my_topic_1.log
SUB 0 my_topic_2 my_topic_2.log

# This script doesn't end until user kill the process (i.e. Ctrl+C)