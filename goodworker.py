#!/usr/bin/env python3
import logging, os, sys, keyboard, pyautogui
from datetime import datetime, timedelta
from notifier import Notifier

FORMAT = '%(levelname)s:    %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

class GoodWorker(object):

    def __init__(self):
        pass

gd = GoodWorker()
