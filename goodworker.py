#!/usr/bin/env python3
import logging, os, sys, keyboard, pyautogui, json, time, random, threading
from datetime import datetime, timedelta
from notifier import Notifier

FORMAT = '%(levelname)s:    %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

class GoodWorker(object):

    HOTKEY_STATUS_CHANGE = 'ctrl + shift + < + >'
    HOTKEY_TERMINATE_PROGRAM = 'ctrl + shift + k + l'
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    ACTIONS_PAUSE =

    def __init__(self):
        self._running = True
        self.active = False
        self.config = self.load_config()
        self.emojies = self.load_emojies()
        self.notifier = Notifier(chat_id=self.config["telegram"]["chat_id"], token=self.config["telegram"]["token"])
        self.session = None
        self.threads = []

        self.actions = ["type_code", "scroll", "click"]

        t = threading.Thread(target=self.run)
        self.threads.append(t)

        for t in self.threads:
            t.start()

    def load_config(self):
        try:
            with open('config', 'r') as f:
                c = json.loads(f.read())
                assert c
                assert "telegram" in c
                assert "chat_id" in c["telegram"]
                assert "token" in c["telegram"]
                return c
        except Exception as e:
            logging.error(e)
            sys.exit()

    def load_emojies(self):
        backup = ["(✧≖‿ゝ≖)"]
        try:
            with open('emojies.txt', 'r') as f:
                content = f.read().split('\n')
                if not content:
                    return backup
                return content
        except Exception as e:
            logging.error(e)
            return backup

    def status_change(self, force_quit=False):
        if not self.active and not force_quit:
            self.active = True
            self.session = self.get_empty_session()
            self.notifier.send_message()
            self.start_working()
        else:
            if self.active:
                self.active = False
                self.session["stopped_at"] = datetime.now()
                logging.debug(self.session)
                self.session["active_time"] = self.calculate_active_time(start=self.session["started_at"], stop=self.session["stopped_at"])
                self.notifier.send_message(action='stop', active_time=self.session["active_time"])

    def get_empty_session(self):
        return {
            "started_at": datetime.now(),
            "stopped_at": None,
            "active_time": None
        }

    def calculate_active_time(self, start, stop):
        total_sec = (stop - start).total_seconds()
        return str(total_sec) + ' seconds'

    def run(self):
        self.notifier.send_message("GoodWorker is working hard")
        time.sleep(0.7)
        self.notifier.send_message("To activate or terminate session press {} at the same time".format(self.HOTKEY_STATUS_CHANGE))
        time.sleep(0.9)
        self.notifier.send_message("To force quit and kill proccess press {}".format(self.HOTKEY_TERMINATE_PROGRAM))
        keyboard.add_hotkey(self.HOTKEY_STATUS_CHANGE, lambda: self.status_change())
        keyboard.add_hotkey(self.HOTKEY_TERMINATE_PROGRAM, lambda: self.exit())
        while self._running:
            time.sleep(5)

    def exit(self):
        self.status_change(force_quit=True)
        self.notifier.send_message("GoodWorker terminated")
        self.notifier.send_message("Bye\n{}".format(random.choice(self.emojies)))
        self._running = False
        sys.exit()

    def send_keys(self, message):
        keyboard.press_and_release('escape')
        keyboard.write(message)

    def start_working(self):
        while self.active:
            random.choice(self.actions)()
            time.sleep(random.randint())


gd = GoodWorker()
