#!/usr/bin/env python3
import logging, os, sys, keyboard, pyautogui, json, time, random, threading, requests
from datetime import datetime, timedelta
from notifier import Notifier
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

FORMAT = '%(levelname)s:    %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

pyautogui.FAILSAFE = True

class GoodWorker(object):

    HOTKEY_STATUS_CHANGE = 'ctrl + shift + < + >'
    HOTKEY_TERMINATE_PROGRAM = 'ctrl + shift + k + l'
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    ACTIONS_TIME_SLEEP_RANGE = (1, 30)

    TREE_LIST_GITHUB = (By.XPATH, "//div[contains(@class, 'repository-content')]/fuzzy-list")
    # TREE_LIST_GITHUB = (By.XPATH, '.js-tree-finder')

    def __init__(self):

        # options = Options()
        # options.headless = False
        # self.browser = webdriver.Firefox(options=options)
        # self.browser.implicitly_wait(10)

        self._running = True
        self.active = False
        self.config = self.load_config()
        self.emojies = self.load_emojies()
        self.code_archive = self.load_code()
        # self.browser.quit()
        self.notifier = Notifier(chat_id=self.config["telegram"]["chat_id"], token=self.config["telegram"]["token"])
        self.session = None
        self.threads = []

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
                assert "projects" in c
                assert c["telegram"]
                assert c["projects"]
                assert "chat_id" in c["telegram"]
                assert "token" in c["telegram"]
                return c
        except Exception as e:
            logging.error("There was an error loading config file")
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

    def load_code(self):

        list_of_files = self.get_project_files(self.config["projects"][0])
        if list_of_files:
            for file in list_of_files:
                self.code_archive.append(self.load_file(project=project, file_name=file))
        # for project in self.config["projects"]:
        #     list_of_files = self.get_project_files(project)
        #     if list_of_files:
        #         for file in list_of_files:
        #             self.code_archive.append(self.load_file(project=project, file_name=file))

    def get_project_files(self, project):
        base_url = 'https://github.com'

        r = requests.get(base_url + "/" + project + '/find/master')
        if r.status_code == 200:
            soup = self.make_soup(r.text)
            data_url = soup.select_one('fuzzy-list[data-url]')["data-url"]
            r = requests.get(base_url + data_url)
            if r.status_code == 200:
                logging.debug(r.content)

    def make_soup(self, html):
        return BeautifulSoup(html,'html.parser')

    def status_change(self, force_quit=False):
        if not self.active and not force_quit:
            self.active = True
            self.session = self.get_empty_session()
            self.notifier.send_message()
            t = threading.Thread(target=self.start_working)
            self.threads.append(t)
            t.start()
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
        keyboard.write(message)

    def get_random_code(self, max_length):
        s = "some code"
        return s[:max_length]

    def type_code(self):
        logging.info("Typing some code")
        s = self.get_random_code(max_length=random.randint(5,450))
        keyboard.press_and_release('escape')
        for char in s:
            self.send_keys(char)
            time.sleep(random.uniform(0.0067, 0.6))

    def scroll(self):
        logging.info("Scrolling")
        pyautogui.scroll(random.randint(-50,50), x=random.randint(1, self.SCREEN_WIDTH), y=random.randint(1, self.SCREEN_HEIGHT))

    def click(self):
        logging.info("Clicking")
        if random.random() < 0.8:
            logging.debug("Left click")
            button = 'left'
        else:
            logging.debug("Right click")
            button = 'right'
        pyautogui.click(x=random.randint(1, self.SCREEN_WIDTH), y=random.randint(1, self.SCREEN_HEIGHT), clicks=random.randint(1,3), interval=random.uniform(0.3, 5), button=button)

    def start_working(self):
        logging.info("Started working session")
        while self.active:
            int = random.random()
            logging.debug(int)
            if int < 0.5:
                t = threading.Thread(target=self.type_code)
                self.threads.append(t)
                t.start()
            elif 0.5 < int < 0.9:
                self.scroll()
            elif int >= 0.9:
                self.click()

            time.sleep(random.randint(*self.ACTIONS_TIME_SLEEP_RANGE))

gd = GoodWorker()
