# Setup Broker MQTT
CONNECT test.mosquitto.org 1883

# Subscribe to multiple topics and store received messages to same log file
SUB 0 my_topic_1 received_msgs.log
SUB 0 my_topic_2 received_msgs.log
SUB 0 my_topic_3 received_msgs.log

# Subscribe to another topic and store received messages to other log file
SUB 0 my_topic_4 other_file.log

# This script doesn't end until user kill the process (i.e. Ctrl+C)