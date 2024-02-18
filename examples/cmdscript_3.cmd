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