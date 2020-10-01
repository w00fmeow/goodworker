#!/usr/bin/env python3
import logging, os, sys, keyboard, pyautogui, json, time, random, threading, requests, re
from datetime import datetime, timedelta
from notifier import Notifier
from bs4 import BeautifulSoup
# import selenium.webdriver as webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By

FORMAT = '%(levelname)s:    %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

pyautogui.FAILSAFE = True

class GoodWorker(object):

    HOTKEY_STATUS_CHANGE = 'ctrl + shift + < + >'
    HOTKEY_TERMINATE_PROGRAM = 'ctrl + shift + k + l'
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    # send notification every 10 min
    NOTIFICATION_TIME = 15
    ACTIONS_TIME_SLEEP_RANGE = (1, 25)

    # FILE_LIST_GITHUB = (By.CSS_SELECTOR, '.d-inline-block.js-tree-browser-result-path')

    def __init__(self):

        # options = Options()
        # options.headless = True
        # self.browser = webdriver.Firefox(options=options)
        # self.browser.implicitly_wait(10)

        self._running = True
        self.active = False
        self._typing = False

        self.config = self.load_config()
        self.actions = self.configure_actions(self.config["actions"])
        self.emojies = self.load_emojies()
        self.code_archive = self.load_code()

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
                # assert "projects" in c
                # assert "file_types" in c
                assert "actions" in c
                assert c["telegram"]
                assert c["actions"]
                assert isinstance(c["actions"], list)
                assert len(c["actions"]) >= 1
                # assert c["file_types"]
                # assert c["projects"]
                assert "chat_id" in c["telegram"]
                assert "token" in c["telegram"]
                if "notifications_every" in c:
                    try:
                        c["notifications_every"] = int(c["notifications_every"])
                        if not c["notifications_every"] or c["notifications_every"] < 0:
                            c.pop("notifications_every")
                    except Exception as e:
                        c.pop("notifications_every")

                if "notifications_every" in c:
                    self.NOTIFICATION_TIME = c["notifications_every"]
                logging.debug(self.NOTIFICATION_TIME)

                return c
        except Exception as e:
            logging.error("There was an error loading config file")
            # self.browser.quit()
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
        try:
            with open('code', 'r') as f:
                return [f.read()]
        except Exception as e:
            logging.error(e)
            sys.exit()
            # return []/

    def configure_actions(self, actions):
        try:
            logging.debug("Raw actions: {}".format(actions))
            assert actions
            assert all(k in a for a in actions for k in ("name", "frequency"))
            assert sum(x["frequency"] for x in actions) == 100
            for a in actions:
                a["frequency"] = a["frequency"]*0.01
            logging.debug("Output actions: {}".format(actions))
            if "type" in actions:
                t = threading.Thread(target=self.load_code)
                self.threads.append(t)
            return actions
        except Exception as e:
            logging.error("There was an error loading actions from file")
            # self.browser.quit()
            sys.exit()

    # def load_code(self):
    #     for project in self.config["projects"]:
    #         list_of_files = self.get_project_files(project)
    #         if list_of_files:
    #             for file in list_of_files:
    #                 raw_file = self.load_raw_file(project=project, file_name=file)
    #                 if raw_file:
    #                     self.code_archive.append(raw_file)

    # def get_project_files(self, project):
    #     l = []
    #     files = self.browser.find_elements(*self.FILE_LIST_GITHUB)
    #     for file in files:
    #         for file_type in self.config["file_types"]:
    #             pat = re.compile(".*\."+file_type)
    #             # logging.debug(file)
    #             # logging.debug(pat)
    #             if re.match(pat, file.text):
    #                 l.append(file.text)
    #     return l

    def load_raw_file(self, project, file_name):
        url = "https://raw.githubusercontent.com/{}/master/{}".format(project, file_name)
        r = requests.get(url)
        if r.status_code == 200:
            return r.text

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
                self.notifier.send_message(action='stop', session=self.session)

    def get_empty_session(self):
        return {
            "started_at": datetime.now(),
            "stopped_at": None,
            "active_time": None,
            "typed": 0,
            "clicks": 0,
            "scrolls": 0,
            "last_notification": datetime.now()
        }

    def calculate_active_time(self, start, stop):
        total_sec = int((stop - start).total_seconds())
        # one second
        if total_sec == 1:
            s = '1 seconds'

        # multiple seconds
        elif 1 < total_sec < 60:
            s = str(total_sec) + ' seconds'

        # one minute
        elif total_sec == 60:
            s = '1 minute'

        # multiple minutes
        elif 60 < total_sec < 60*60:
            s = str(round(total_sec/60, 2)) + ' minutes'

        # one hour
        elif total_sec == 60*60:
            s = '1 hour'

        # multiple hours
        elif 60*60 < total_sec < 60*60*24:
            s = str(round(total_sec/60/60, 2)) + ' hours'

        # one day
        elif total_sec == 60*60*24:
            s = '1 day'

        # multiple days
        elif 60*60*24 < total_sec:
            # s = str(total_sec/60/60/24) + ' days'
            s = str(round(total_sec/60/60/24, 2)) + ' days'

        return s

    def run(self):
        print("""\

____ ____ ____ ___  _ _ _ ____ ____ _  _ ____ ____
| __ |  | |  | |  \ | | | |  | |__/ |_/  |___ |__/
|__] |__| |__| |__/ |_|_| |__| |  \ | \_ |___ |  \


        """)
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
        # self.browser.quit()
        sys.exit()

    def send_keys(self, message):
        try:
            keyboard.write(message)
            self.session["typed"] += len(message)
        except Exception as e:
            pass

    def get_random_code(self, max_length):
        return random.choice(self.code_archive)[:max_length]

    def type_code(self):
        logging.info("Typing some code")
        self._typing = True
        s = self.get_random_code(max_length=random.randint(2,6))
        keyboard.press_and_release('escape')
        for char in s:
            if not self.active:
                break
            self.send_keys(char)
            time.sleep(random.uniform(0.0067, 0.6))
        self._typing = False

    def scroll(self):
        logging.info("Scrolling")
        for _ in range(0, random.randint(1,5)):
            pyautogui.scroll(random.randint(-25,-5), x=random.randint(1, self.SCREEN_WIDTH), y=random.randint(1, self.SCREEN_HEIGHT))
            self.session["scrolls"] += 1
            time.sleep(random.uniform(0.1, 1.9))

        for _ in range(0, random.randint(1,2)):
            pyautogui.scroll(random.randint(5,20))
            self.session["scrolls"] += 1
            time.sleep(random.uniform(0.1, 1.3))

    def click(self):
        # if random.random() < 0.8:
        #     logging.debug("Left click")
        #     button = 'left'
        # else:
        #     logging.debug("Right click")
        #     button = 'right'
        logging.debug("Left click")
        button = 'left'
        for _ in range(0, random.randint(1, 2)):
            x = random.randint(int(self.SCREEN_WIDTH*0.17), self.SCREEN_WIDTH-int(self.SCREEN_WIDTH*0.17))
            y = random.randint(self.SCREEN_HEIGHT-int(self.SCREEN_HEIGHT*0.8), int(self.SCREEN_HEIGHT*0.3))
            pyautogui.moveTo(x, y, random.uniform(0.3, 0.9))
            c = random.randint(1,2)
            pyautogui.click(x=x, y=y, clicks=c, interval=random.uniform(0.3, 0.7), button=button)
            self.session["clicks"] += c

    def start_working(self):
        def execute_action(action_name):
            if action_name == "type":
                if not self._typing:
                    t = threading.Thread(target=self.type_code)
                    self.threads.append(t)
                    t.start()
            elif action_name == 'click':
                self.click()
            elif action_name == 'scroll':
                self.scroll()

        logging.info("Started working session")
        while self.active:
            n = random.random()
            logging.debug("N: {}".format(n))
            if len(self.actions) == 1:
                execute_action(self.actions[0]["name"])
            elif len(self.actions) == 2:
                if n <= self.actions[0]["frequency"]:
                    execute_action(self.actions[0]["name"])
                else:
                    execute_action(self.actions[1]["name"])
            elif len(self.actions) == 3:
                if n <= self.actions[0]["frequency"]:
                    execute_action(self.actions[0]["name"])
                elif self.actions[0]["frequency"] <= n <= self.actions[0]["frequency"] + self.actions[1]["frequency"]:
                    execute_action(self.actions[1]["name"])
                else:
                    execute_action(self.actions[2]["name"])

            diff = datetime.now() - self.session["last_notification"]

            if diff > timedelta(minutes=self.NOTIFICATION_TIME):
                self.session["last_notification"] = datetime.now()
                self.notifier.send_message("Session is active already {}".format(self.calculate_active_time(start=self.session["started_at"], stop=datetime.now())))

            time.sleep(random.randint(*self.ACTIONS_TIME_SLEEP_RANGE))

gd = GoodWorker()
