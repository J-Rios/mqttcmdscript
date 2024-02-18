# -*- coding: utf-8 -*-

'''
Script:
    texts.py
Description:
    Texts file
Author:
    Jose Miguel Rios Rubio
Date:
    18/02/2024
Version:
    1.0.0
'''

###############################################################################
# Texts
###############################################################################

class TEXT():
    '''
    Texts of mqttcmdscript tool.
    '''

    OPT_FILE = \
        "\n" \
        "Specify the cmdscript file to parse and use."

    NO_ARGS = \
        "\n" \
        "Specify the cmdscript file to use."

    INVALID_CMDSCRIPT = \
        "\n" \
        "Invalid cmdscript."

    CMDSCRIPT_MISSING_ARG = \
        "Missing argument on arg %s"

    CMDSCRIPT_INVALID_ARG = \
        "Invalid argument on arg %s: %s"

    BAD_OPTION = \
        "\n" \
        "Invalid arguments provided. Check --help information about usage."

    UNEXPECTED_CMDSCRIPT_CMD = \
        "Ignoring unknown command found in cmdscript: %s"

    INVALID_CMDSCRIPT_CMD = \
        "Ignoring invalid cmdscript command: %s"

    HELP = \
        "\n" \
        "NAME\n" \
        "    mqttcmdscript {}\n" \
        "\n" \
        "SYNOPSIS\n" \
        "    python mqttcmdscript.py [--help] [--version] " \
        "[-f <CMDSCRIPT_FILE>]\n" \
        "\n" \
        "DESCRIPTION\n" \
        "    Python tool that parse a \"cmdscript\" text file provided by\n" \
        "    the user to automate and execute the specified MQTT client \n" \
        "    instructions to subscribe and publish messages to different \n" \
        "    MQTT Broker topics.\n" \
        "\n" \
        "OPTIONS\n" \
        "    -h, --help\n" \
        "        Shows help text (current information).\n" \
        "\n" \
        "    -f --file\n" \
        "        Specify the cmdscript file to use.\n" \
        "\n" \
        "    -v, --version\n" \
        "        Shows current installed version.\n" \
        "\n" \
        "AUTHOR\n" \
        "    {}\n" \
        "\n" \
        "PROJECT REPOSITORY\n" \
        "    {}\n" \
        "\n" \
        "DONATION\n" \
        "    Do you like this program, buy me a coffee:\n" \
        "    {}\n" \
        "\n"
