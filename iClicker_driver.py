import json
import selenium.common
import seleniumwire.request
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from threading import Thread
from threading import Event

class iClicker_driver:
    REQUEST_URL: str = 'https://api.iclicker.com/student/course/status'
    LOG_IN_URL: str = 'https://student.iclicker.com/#/login'
    COURSES_URL: str = 'https://student.iclicker.com/#/courses'
    JOIN_BTN_ID: str = 'btnJoin'

    def __init__(self, config_file: str = 'config.json', auto_wait: bool = True):
        self.joinUp: bool = False
        self.driver: webdriver.Chrome = webdriver.Chrome(
            seleniumwire_options={
                'exclude_hosts': ['eum-us-west-2.instana.io', 'analytic.rollout.io', 'accounts.google.com',
                                  'www.google-analytics.com',
                                  'iclicker-prod-inst-analytics.macmillanlearning.com'],
                'ignore_http_methods': ['GET', 'HEAD', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE',
                                        'PATCH']})
        self.driver.response_interceptor = self.response_interceptor
        with open(config_file, 'r') as f:
            self.config: dict = json.load(f)
        self.account_name: str = ''
        self.event: Event = Event()
        self.auto_wait = auto_wait
        self.wait_thread: Thread = Thread(name='WaitForMeeting',target=self.wait_for_meeting)

    def start(self):
        try:
            if not self.account_name:
                self.get_account()
        except ValueError:
            print("Couldn't find email or password in config file. Not starting...")
        self.driver.get(self.LOG_IN_URL)
        self.wait_for_ajax()
        self.log_in()

    def log_in(self):
        # Logs in
        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, 'userEmail'))) \
            .send_keys(self.config[self.account_name]['Email'])
        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, 'userPassword'))) \
            .send_keys(self.config[self.account_name]['Password'])
        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, 'sign-in-button'))).click()
        self.wait_for_ajax()
        self.driver.implicitly_wait(5)

    def navigate_to_course(self, course: str):
        # This XPath searches for the course button by the text contained within.
        # Unfortunately the buttons don't have descriptive IDs, so we have to use XPath
        WebDriverWait(self.driver, 20) \
            .until(ec.element_to_be_clickable((By.XPATH,
                                               f'/html/body/div/div/div/div/div/main/div/ul/li/a[label[text() = '
                                               f'\'{self.config[self.account_name]["Course"][course]}\']]'))).click()
        del self.driver.requests
        if self.auto_wait:
            self.start_wait()

    def start_wait(self):
        self.wait_thread.start()

    def wait_for_meeting(self):
        while True:
            self.event.wait()
            if self.joinUp:
                break
        self.event.clear()
        self.wait_for_ajax()
        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, self.JOIN_BTN_ID))).click()
        # three-dot-loader
        WebDriverWait(self.driver, 20).until(ec.invisibility_of_element((By.ID,'three-dot-loader')))

    def get_account(self):
        self.account_name = input('Enter the account name to use (i.e., the account name in config.json)')
        if self.account_name not in self.config or 'Email' not in self.config[self.account_name] or 'Password' not in \
                self.config[self.account_name]:
            raise ValueError("Could not find email or password in config file.")

    def wait_for_ajax(self):
        WebDriverWait(self.driver, 20).until(lambda d: self.driver.execute_script("return jQuery.active == 0"))

    def response_interceptor(self, request: seleniumwire.request.Request, response: seleniumwire.request.Response):
        if request.url == self.REQUEST_URL:
            body = response.body.decode()
            if self.joinUp:
                if body[63:67] == 'null':
                    self.joinUp = False
            elif body[63:67] != 'null':
                self.joinUp = True
                self.event.set()
