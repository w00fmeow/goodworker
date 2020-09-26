#!/usr/bin/env python3
import os, sys, logging, requests
from datetime import datetime

FORMAT = '%(levelname)s:    %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

class Notifier(object):
    def __init__(self, chat_id, token):
        self.chat_id = chat_id
        self.base_url = "https://api.telegram.org/bot{0}/sendMessage".format(token)

    def send_message(self, message=None, action='start', active_time=None):
        logging.debug("message: {}, action: {}".format(message, action))
        if not message:
            if not action:
                action = 'start'
            message = self.get_message(action=action, active_time=active_time)
        data = {}
        data["text"] = message
        data["chat_id"] = self.chat_id
        logging.debug("data: {}".format(data))
        try:
            r = requests.post(self.base_url, data=data)
        except Exception as e:
            logging.error(e)

    def get_message(self, action, active_time=None):
        s = 'Good worker'
        if action == 'start':
            s += ' started'
        elif action == 'stop':
            s += ' stopped'
        s += ' session.'
        if active_time:
            s += ' Session was active {}'.format(active_time)
        return s
