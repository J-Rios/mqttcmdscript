# -*- coding: utf-8 -*-

'''
Script:
    constants.py
Description:
    Constants file.
Author:
    Jose Miguel Rios Rubio
Date:
    18/02/2024
Version:
    1.0.0
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# System Operation Library
from os import path as os_path


###############################################################################
# Constants
###############################################################################

# Program return codes
class RC():
    OK = 0
    FAIL = -1
    NO_ARGS = -2


# Constants
class CONST():

    # Current Log level to use
    LOG_LEVEL = logging.INFO

    # Log File
    LOG_FILE = "mqttcmdscript.log"

    # Log timestamp format
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Application Version
    APP_VERSION = "1.0.0 (18/02/2024)"

    # Main Developer
    AUTHOR = "Jose Miguel Rios Rubio"

    # Project code repository
    PROJECT_REPO = "https://github.com/J-Rios/mqttcmdscript"

    # Developer donation address
    DEV_DONATE = "https://www.paypal.com/paypalme/josrios"

    # Actual constants.py full path directory name
    SCRIPT_PATH = os_path.dirname(os_path.realpath(__file__))

    # Input arguments flags
    OPTIONS = \
    [
        "-h", "--help",
        "-f", "--file",
        "-v", "--version"
    ]

    # Supported cmdscript commands
    CMDSCRIPT_COMMANDS = \
    [
        "CFG_CLIENT_ID",
        "CFG_CLEAN_SESSION",
        "CFG_KEEPALIVE",
        "CFG_USER",
        "CFG_USE_TLS",
        "CFG_TLS_CERT",
        "CFG_PUB_EACH",
        "CONNECT",
        "DISCONNECT",
        "DELAY",
        "DELAY_MS",
        "DELAY_H",
        "PUB",
        "SUB"
    ]

    # Common Serial BaudRates
    CMDSCRIPT_ARGS_YES_NO = ["YES", "NO"]
