#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    mqttcmdscript.py
Description:
    Python tool that parse a "cmdscript" text file provided by the user
    to automate and execute the specified MQTT client instructions to
    subscribe and publish messages to different MQTT Broker topics.
Author:
    Jose Miguel Rios Rubio
Creation date:
    17/02/2024
Last modified date:
    18/02/2024
Version:
    1.0.0
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# Arguments Parser Library
from argparse import ArgumentParser

# Date and Time Library
from datetime import datetime

# System Signals Library
from platform import system as os_system
from signal import signal, SIGTERM, SIGINT
if os_system() != "Windows":
    from signal import SIGUSR1

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

# Threads Library
from threading import Thread

# Time Library
from time import time, sleep

# Error Traceback Library
from traceback import format_exc

# Universal Unique Identifier Library
from uuid import uuid4 as generate_uuid


###############################################################################
# Third-Party Libraries
###############################################################################

# Image Captcha Generator Library
from paho.mqtt import client as mqtt


###############################################################################
# Local Libraries
###############################################################################

# Constants Library
from constants import CONST, RC

# Files Read-Write Library
from filesrw import file_read_all_text, file_write_text_line

# Texts Library
from texts import TEXT


###############################################################################
# Logger Setup
###############################################################################

logging.basicConfig(
    level=CONST.LOG_LEVEL,
    format=CONST.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CONST.LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)


###############################################################################
# Auxiliary Elements
###############################################################################

class Command():
    cmd = ""
    args: list[str] = []


class PublishInfo():
    topic = ""
    msg = ""


class ConfigSubscription():
    qos = 0
    topic = ""
    logfile = ""


class ConfigPublishEach():
    each = 60
    qos = 0
    topic = ""
    msg = ""
    time_last_pub = 0


class Configuration():
    invalid = False
    commands: list[Command] = []
    mqtt_host = ""
    mqtt_port = 1883
    clean_session = True
    keepalive_s = 60
    client_id = ""
    username = ""
    password = ""
    use_tls = False
    tls_cert = ""
    tls_key = ""
    subscriptions: list[ConfigSubscription] = []
    pub_each: list[ConfigPublishEach] = []
    steps_to_execute: list[Command] = []


###############################################################################
# Global Elements
###############################################################################

app_exit = False
mqtt_connection_lost = False
time_mqtt_connected: int | None = None
t_wait_start: int | None = None
config = Configuration()


###############################################################################
# Auxiliary Functions
###############################################################################

def is_int(s, base=10):
    '''
    Check if provided string is an integer number.
    '''
    try:
        int(s, base)
        return True
    except ValueError:
        return False


def get_timestamp():
    '''
    Get current UTC time and create a timestamp string from it.
    '''
    timestamp = ""
    try:
        tobj = datetime.utcnow()
        timestamp = "[{}.{}]".format(
            tobj.strftime("[%Y-%m-%d_%H:%M:%S"), tobj.strftime("%f")[:3])
    except Exception:
        logger.error(format_exc())
        logger.error("Fail to get current time and create timestamp\n")
    return timestamp


###############################################################################
# MQTT Callbacks
###############################################################################

def cb_mqtt_on_connect(client, userdata, flags, reason_code, properties):
    '''
    Callback that is triggered when the MQTT Connection is done.
    It make the subscription to all of the configured topics.
    '''
    global mqtt_connection_lost
    global time_mqtt_connected
    timestamp = get_timestamp()
    to_write = f"{timestamp} -- MQTT Connected --"
    if mqtt_connection_lost:
        to_write = f"{timestamp} -- MQTT Connected (Communication Restored) --"
    for sub in config.subscriptions:
        file_write_text_line(sub.logfile, to_write)
    mqtt_connection_lost = False
    time_mqtt_connected = time()
    logger.info("MQTT connected to Broker")
    for sub in config.subscriptions:
        client.subscribe(sub.topic, sub.qos)


def cb_mqtt_on_disconnect(client, userdata, flags, reason_code, properties):
    '''
    Callback that is triggered when the MQTT is Disconnected or MQTT
    communication is lost.
    It writes disconnection message to all subscribed log files.
    '''
    global mqtt_connection_lost
    if not mqtt_connection_lost:
        mqtt_connection_lost = True
        logger.info("MQTT disconnected from Broker")
        if reason_code != 0:
            timestamp = get_timestamp()
            to_write = f"{timestamp} -- MQTT Communication Lost --"
            for sub in config.subscriptions:
                file_write_text_line(sub.logfile, to_write)


def cb_mqtt_on_msg_rx(client, userdata, msg):
    '''
    Callback to handle a MQTT message received.
    It checks form the configured list of topics subscriptions and write
    the message payload to the corresponding log file.
    '''
    payload_str = msg.payload.decode("utf-8")
    logger.info("Received msg - [Topic: %s] [Payload: %s]",
                 msg.topic, payload_str)
    for sub in config.subscriptions:
        if sub.topic == msg.topic:
            timestamp = get_timestamp()
            to_write = f"{timestamp} [{msg.topic}] {payload_str}"
            file_write_text_line(sub.logfile, to_write)


###############################################################################
# MQTT Process Thread (Required to publish msg on callbacks)
###############################################################################

def th_mqtt_process(mqtt_client):
    mqtt_client.loop_forever()


###############################################################################
# CMDSCRIPT Interpreter Functions
###############################################################################

def manage_publish_each_time(mqtt_client):
    '''
    Manage list of CMDSCRIPT configured message to publish periodically
    each specified time.
    '''
    for i, pub_each in enumerate(config.pub_each):
        if pub_each.time_last_pub is None:
            pub_each.time_last_pub = time_mqtt_connected
        if time() - pub_each.time_last_pub >= pub_each.each:
            logger.info(
                "Publish msg each %d - [Qos: %d] [Topic: %s] [Payload: %s]",
                pub_each.each, pub_each.qos, pub_each.topic, pub_each.msg)
            mqtt_client.publish(pub_each.topic, pub_each.msg,
                                pub_each.qos)
            pub_each.time_last_pub = time()
            config.pub_each[i] = pub_each


def run_step_cmd(mqtt_client, cmd_arg):
    '''
    Run an iteration over the list of CMDSCRIPT configured commands to
    execute. If the command is completed, return true, otherwise return
    false.
    '''
    global app_exit
    global t_wait_start
    if cmd_arg.cmd == "DISCONNECT":
        logger.info("Disconnect")
        mqtt_client.disconnect()
        app_exit = True
        return True
    elif cmd_arg.cmd == "PUB":
        qos = cmd_arg.args[0]
        topic = cmd_arg.args[1]
        msg = cmd_arg.args[2]
        logger.info("Publish msg - [Qos: %d] [Topic: %s] [Payload: %s]",
                     qos, topic, msg)
        mqtt_client.publish(topic, msg, qos)
        return True
    elif (cmd_arg.cmd == "DELAY") or \
    (cmd_arg.cmd == "DELAY_MS") or cmd_arg.cmd == "DELAY_H":
        wait_t = cmd_arg.args[0]
        if cmd_arg.cmd == "DELAY_MS":
            wait_t = cmd_arg.args[0] / 1000
        elif cmd_arg.cmd == "DELAY_H":
            wait_t = cmd_arg.args[0] * 3600
        if t_wait_start is None:
            t_wait_start = time()
            logger.info("Delay wait %d sec", wait_t)
        if time() - t_wait_start >= wait_t:
            logger.info("Delay wait done")
            t_wait_start = None
            return True
    return False


def cmdscript_interpreter():
    '''CMDSCRIPT interpreter.'''
    # Launch MQTT Connection
    logger.info("Launching MQTT Connection...")
    if config.client_id == "":
        uuid = generate_uuid()
        config.client_id = f"mqttcmdscript_{uuid}"
    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=config.client_id,
        clean_session=config.clean_session)
    mqtt_client.enable_logger(logger)
    mqtt_client.on_connect = cb_mqtt_on_connect
    mqtt_client.on_disconnect = cb_mqtt_on_disconnect
    mqtt_client.on_message = cb_mqtt_on_msg_rx
    mqtt_client.connect(config.mqtt_host, config.mqtt_port, config.keepalive_s)
    th_mqtt_process_id = Thread(target=th_mqtt_process, args=(mqtt_client,))
    th_mqtt_process_id.start()
    step = 0
    while not app_exit:
        if mqtt_client.is_connected():
            # Manage Publish each time
            manage_publish_each_time(mqtt_client)
            # Execute steps instructions
            if step < len(config.steps_to_execute):
                if run_step_cmd(mqtt_client, config.steps_to_execute[step]):
                    step = step + 1
        sleep(0.10)
    # Close MQTT and wait for process thread end
    logger.info("Disconnecting from MQTT")
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    if th_mqtt_process_id.is_alive():
        th_mqtt_process_id.join()
    logger.info("MQTT Closed")
    return RC.OK


###############################################################################
# CMDSCRIPT Parser Functions
###############################################################################

def cmdscript_parse(cmdscript):
    '''
    Parse CMDSCRIPT information, check for unexpected or unsupported
    keywords, and populate all the configuration from the script to
    return it.
    '''
    # DOS to UNIX EOLs
    cmdscript = cmdscript.replace("\r\n", "\n")
    # Split the text in lines
    cmdscript = cmdscript.split("\n")
    # Iterate over each line detecting which ones must be ignored
    lines_to_rm_index = []
    for i in range(len(cmdscript)-1):
        line = cmdscript[i]
        # Check for empty and comment lines
        if (len(line) == 0) or (line[0] == "#"):
            lines_to_rm_index.append(i)
            continue
        # Check for unsupported/unknown command
        if line.split()[0] not in CONST.CMDSCRIPT_COMMANDS:
            logger.warning(TEXT.UNEXPECTED_CMDSCRIPT_CMD, line)
            lines_to_rm_index.append(i)
            continue
    # Remove lines to ignore from cmdscript
    removed = 0
    for i in lines_to_rm_index:
        del cmdscript[i-removed]
        removed = removed + 1
    # Populate List of Commands on Configuration element
    for cmd_line in cmdscript:
        cmd_arg = Command()
        words = cmd_line.split(" ")
        cmd_arg.cmd = words[0].upper()
        cmd_arg.args = words[1:]
        config.commands.append(cmd_arg)
    # Parse commands to create config information structure
    for cmd_arg in config.commands:
        if cmd_arg.cmd == "CFG_CLIENT_ID":
            if len(cmd_arg.args) == 0:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            config.client_id = cmd_arg.args[0]
        elif cmd_arg.cmd == "CFG_CLEAN_SESSION":
            if len(cmd_arg.args) == 0:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if cmd_arg.args[0] not in CONST.CMDSCRIPT_ARGS_YES_NO:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            if cmd_arg.args[0].upper() == "YES":
                config.clean_session = True
            elif cmd_arg.args[0].upper() == "NO":
                config.clean_session = False
        elif cmd_arg.cmd == "CFG_KEEPALIVE":
            if len(cmd_arg.args) == 0:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if is_int(cmd_arg.args[0]) == False:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            config.keepalive_s = int(cmd_arg.args[0])
        elif cmd_arg.cmd == "CFG_USER":
            if len(cmd_arg.args) < 2:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            config.username = cmd_arg.args[0]
            config.password = cmd_arg.args[1]
        elif cmd_arg.cmd == "CFG_TLS_CERT":
            if len(cmd_arg.args) < 2:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            config.tls_cert = cmd_arg.args[0]
            config.tls_key = cmd_arg.args[1]
        elif cmd_arg.cmd == "CFG_USE_TLS":
            if len(cmd_arg.args) == 0:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if cmd_arg.args[0] not in CONST.CMDSCRIPT_ARGS_YES_NO:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            if cmd_arg.args[0].upper() == "YES":
                config.use_tls = True
            elif cmd_arg.args[0].upper() == "NO":
                config.use_tls = False
        elif cmd_arg.cmd == "CFG_PUB_EACH":
            if len(cmd_arg.args) < 4:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if (is_int(cmd_arg.args[0]) == False) or \
            (is_int(cmd_arg.args[1]) == False):
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            msg = " ".join(cmd_arg.args[3:])
            if (len(msg) < 3) or (msg[0] != "\"") or (msg[-1] != "\""):
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            cfg_pub_each = ConfigPublishEach()
            cfg_pub_each.each = int(cmd_arg.args[0])
            cfg_pub_each.qos = int(cmd_arg.args[1])
            cfg_pub_each.topic = cmd_arg.args[2]
            cfg_pub_each.msg = msg[1:-1]
            config.pub_each.append(cfg_pub_each)
        elif cmd_arg.cmd == "SUB":
            if len(cmd_arg.args) < 3:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if is_int(cmd_arg.args[0]) == False:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            cfg_sub = ConfigSubscription()
            cfg_sub.qos = int(cmd_arg.args[0])
            cfg_sub.topic = cmd_arg.args[1]
            cfg_sub.logfile = cmd_arg.args[2]
            config.subscriptions.append(cfg_sub)
        elif cmd_arg.cmd == "CONNECT":
            if len(cmd_arg.args) < 2:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                continue
            if is_int(cmd_arg.args[1]) == False:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                continue
            config.mqtt_host = cmd_arg.args[0]
            config.mqtt_port = int(cmd_arg.args[1])
    # Parse commands to create step by step instructions
    for cmd_arg in config.commands:
        if cmd_arg.cmd == "DISCONNECT":
            config.steps_to_execute.append(cmd_arg)
        if cmd_arg.cmd == "PUB":
            if len(cmd_arg.args) < 3:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                break
            if is_int(cmd_arg.args[0]) == False:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                break
            msg = " ".join(cmd_arg.args[2:])
            if (len(msg) < 3) or (msg[0] != "\"") or (msg[-1] != "\""):
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                break
            cmd_arg.args = cmd_arg.args[:2]
            cmd_arg.args[0] = int(cmd_arg.args[0])
            cmd_arg.args.append(msg[1:-1])
            config.steps_to_execute.append(cmd_arg)
        elif (cmd_arg.cmd == "DELAY") or \
        (cmd_arg.cmd == "DELAY_MS") or cmd_arg.cmd == "DELAY_H":
            if len(cmd_arg.args) == 0:
                logger.error(TEXT.CMDSCRIPT_MISSING_ARG, cmd_arg.cmd)
                config.invalid = True
                break
            if is_int(cmd_arg.args[0]) == False:
                logger.error(TEXT.CMDSCRIPT_INVALID_ARG,
                             cmd_arg.cmd, cmd_arg.args)
                config.invalid = True
                break
            cmd_arg.args[0] = int(cmd_arg.args[0])
            config.steps_to_execute.append(cmd_arg)
    return config


###############################################################################
# Arguments Parser
###############################################################################

def parse_options():
    '''Get and parse program input arguments.'''
    parser = ArgumentParser()
    parser.version = CONST.APP_VERSION
    parser.add_argument("-v", "--version", action="version")
    parser.add_argument("-f", "--file", action="store", nargs=1, type=str,
                        required=True, help=TEXT.OPT_FILE)
    args = parser.parse_args()
    return args


###############################################################################
# Main Function
###############################################################################

def main(argc, argv):
    '''
    Main Function.
    '''
    # Check and parse input arguments
    if argc == 0:
        text_help = TEXT.HELP.format(CONST.APP_VERSION, CONST.AUTHOR,
                                     CONST.PROJECT_REPO, CONST.DEV_DONATE)
        print(text_help)
        return RC.NO_ARGS
    options = parse_options()
    path_cmdscript = options.file[0]
    # Read cmdscript text file
    cmdscript = file_read_all_text(path_cmdscript)
    if cmdscript == "":
        return RC.FAIL
    # Parse cmdscript instructions
    cmdscript_parse(cmdscript)
    logger.debug(config)
    if config.invalid:
        logger.info(TEXT.INVALID_CMDSCRIPT)
        return RC.FAIL
    # Launch cmdscript interpreter
    return cmdscript_interpreter()


###############################################################################
# Exit Function
###############################################################################

def program_exit(return_code):
    '''
    Program exit function.
    '''
    logger.debug("Application Exit (%d)", return_code)
    sys_exit(return_code)


###############################################################################
# System Termination Signals Management
###############################################################################

def system_termination_signal_handler(signal,  frame):
    '''
    Termination signals detection handler. It stop application execution.
    '''
    global app_exit
    app_exit = True


def system_termination_signal_setup():
    '''
    Attachment of System termination signals (SIGINT, SIGTERM, SIGUSR1)
    to function handler.
    '''
    # SIGTERM (kill pid) to signal_handler
    signal(SIGTERM, system_termination_signal_handler)
    # SIGINT (Ctrl+C) to signal_handler
    signal(SIGINT, system_termination_signal_handler)
    # SIGUSR1 (self-send) to signal_handler
    if os_system() != "Windows":
        signal(SIGUSR1, system_termination_signal_handler)


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    system_termination_signal_setup()
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    program_exit(return_code)
