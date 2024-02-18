# -*- coding: utf-8 -*-

'''
Script:
    filesrw.py
Description:
    File system files functions.
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
from os import remove as os_remove
from os import makedirs as os_makedirs
from os import utime as os_utime

# Error Traceback Library
from traceback import format_exc


###############################################################################
# Logger Setup
###############################################################################

logger = logging.getLogger(__name__)


###############################################################################
# File Operation Functions
###############################################################################

def create_parents_dirs(file_path):
    '''
    Create all parents directories from provided file path
    (mkdir -p $file_path).
    '''
    try:
        parentdirpath = os_path.dirname(file_path)
        if parentdirpath != "":
            if not os_path.exists(parentdirpath):
                os_makedirs(parentdirpath, 0o775)
        return True
    except Exception:
        logger.error(format_exc())
        logger.error("Can't create parents dirs of %s.", file_path)
        return False


def file_exists(file_path=None):
    '''Check if the given file exists'''
    # Check if no path provided or file doesnt exists
    if file_path is None:
        return None
    if not os_path.exists(file_path):
        return False
    return True


def file_read_all_bin(file_path):
    '''Read all file content as binary and return it.'''
    # Check if no path provided or file doesnt exists
    if file_path is None:
        return None
    if not os_path.exists(file_path):
        logger.error("File %s not found.", file_path)
        return None
    # File exists, so open and read it
    read = None
    try:
        with open(file_path, "rb") as f:
            read = f.read()
    except Exception:
        logger.error(format_exc())
        logger.error("Can't open and read file %s", file_path)
    return read


def file_read_all_text(file_path):
    '''Read all text file content and return it in a string.'''
    read = ""
    # Check if file doesnt exists
    if not os_path.exists(file_path):
        logger.error("File %s not found.", file_path)
    # File exists, so open and read it
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                read = f.read()
        except Exception:
            logger.error(format_exc())
            logger.error("Can't open and read file %s.", file_path)
    return read


def file_write_text(file_path, text=""):
    '''Write text to provided file.'''
    create_parents_dirs(file_path)
    # Determine if file exists and set open mode to write or append
    if not os_path.exists(file_path):
        logger.info("File %s not found, creating it...", file_path)
    # Try to Open and write to file
    try:
        with open(file_path, 'a', encoding="utf-8") as f:
            f.write(text)
    except Exception:
        logger.error(format_exc())
        logger.error("Can't write to file %s.", file_path)


def file_write_text_line(file_path, text=""):
    '''Write a new line to provided file.'''
    create_parents_dirs(file_path)
    # Determine if file exists and set open mode to write or append
    if not os_path.exists(file_path):
        logger.info("File %s not found, creating it...", file_path)
    # Try to Open and write to file
    try:
        with open(file_path, 'a', encoding="utf-8") as f:
            f.write(f"{text}\n")
    except Exception:
        logger.error(format_exc())
        logger.error("Can't write to file %s.", file_path)


def file_clear(file_path):
    '''Remove and recreate a file to empty file content.'''
    create_parents_dirs(file_path)
    try:
        if os_path.exists(file_path):
            os_remove(file_path)
        with open(file_path, 'a'):
            os_utime(file_path, None)
    except Exception:
        logger.error(format_exc())
        logger.error("Can't clear file %s.", file_path)
