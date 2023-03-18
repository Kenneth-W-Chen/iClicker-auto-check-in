import json
import time
from typing import Union, List

import selenium.common
import seleniumwire.request
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from seleniumwire import webdriver
from threading import Thread
from threading import Lock
from threading import Event
from datetime import datetime
from course_info import hour_minute, course_info


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

        # Config info
        with open(config_file, 'r') as f:
            self.config: dict = json.load(f)
        self.account_name: str = ''

        self.auto_wait = auto_wait

        # For timing
        self.course_schedule: List[course_info] = []
        self.currentCourseIndex = -1
        self.nextCourseIndex = 0

        # This event is to ensure that we didn't get logged out at some point... don't really like this
        self.urlCheckEvent: Event = Event()

        # Thread to wait to join up
        self.wait_thread: Thread = Thread(name='WaitForMeeting', target=self.wait_for_meeting)

        self.time_thread: Thread = Thread(name='CheckTime', target=self.wait_for_time)

        self.time_lock: Lock = Lock() # Thread lock

        self.joinEvent: Event = Event()
        self.restartEvent: Event = Event()
        self.currentCourse: str = ''

    def start(self):
        try:
            if not self.account_name:
                self.get_account()
        except ValueError:
            print("Couldn't find email or password in config file. Not starting...")
        self.set_up_courses()
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
        self.navigate_to_course(self.course_schedule[self.currentCourseIndex].course)
        self.time_thread.start()

    def navigate_to_course(self, course: str):
        self.time_lock.acquire()
        # This XPath searches for the course button by the text contained within.
        # Unfortunately the buttons don't have descriptive IDs, so we have to use XPath
        WebDriverWait(self.driver, 20) \
            .until(ec.element_to_be_clickable((By.XPATH,
                                               f'/html/body/div/div/div/div/div/main/div/ul/li/a[label[text() = '
                                               f'\'{course}\']]'))).click()
        self.currentCourse = course
        del self.driver.requests
        if self.auto_wait:
            self.start_wait()
        self.time_lock.release()

    def start_wait(self):
        self.wait_thread.start()

    def wait_for_meeting(self):
        while True:
            while True:
                self.joinEvent.wait()
                self.time_lock.acquire()
                if self.joinUp:
                    break
                self.time_lock.release()
            self.joinEvent.clear()
            self.wait_for_ajax()
            WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, self.JOIN_BTN_ID))).click()
            # three-dot-loader
            WebDriverWait(self.driver, 20).until(ec.invisibility_of_element((By.ID, 'three-dot-loader')))
            self.time_lock.release()
            # todo: add wait for event to restart
            self.restartEvent.wait()

    def wait_for_time(self):
        if len(self.course_schedule) <= 1:
            return
        nextCourseTime = self.course_schedule[self.nextCourseIndex].ht
        while True:
            now = hour_minute.utcnow()
            if now >= nextCourseTime:
                self.time_lock.acquire()
                if self.driver.current_url != self.COURSES_URL:
                    if self.driver.current_url == self.LOG_IN_URL:
                        self.log_in()
                    else:
                        self.driver.get(self.COURSES_URL)
                self.navigate_to_course(self.course_schedule[self.nextCourseIndex].course)
                self.joinUp = False
                self.joinEvent.clear()
                self.restartEvent.set()
                self.currentCourseIndex = self.nextCourseIndex
                if self.nextCourseIndex == len(self.course_schedule) -1:
                    self.nextCourseIndex = 0
                else:
                    self.nextCourseIndex += 1
                nextCourseTime = self.course_schedule[self.nextCourseIndex].ht

    def wait_for_url_change(self):  # Todo
        while True:
            self.urlCheckEvent.wait()

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
                    # return
            elif body[63:67] != 'null':
                self.joinUp = True
                self.joinEvent.set()
        # Todo: need to figure out if iClicker automatically logs out at some point

    def set_up_courses(self):
        for key, value in self.config[self.account_name]['Courses'].items():
            self.course_schedule.append(course_info(hour_minute.from_str(value['Time']), value['Name']))
        self.course_schedule.sort()
        now = hour_minute.utcnow()
        for i in range(len(self.course_schedule)):
            if now <= self.course_schedule[i]:
                self.nextCourseIndex = i
                break
        if self.nextCourseIndex == 0:
            self.currentCourseIndex = len(
                self.course_schedule) - 1  # Todo: I can't really run this in my head but I think this works
        print('Courses set up')
