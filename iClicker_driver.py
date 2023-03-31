from json import load
from time import sleep

from datetime import datetime
from threading import Thread, Lock, Event
from typing import Union, List

from seleniumwire.request import Request, Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

from course_info import HourMinute, course_info


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
            self.config: dict = load(f)
        self.account_name: str = ''

        self.auto_wait = auto_wait

        # For timing
        self.course_schedule: List[course_info] = []
        self.currentCourseIndex = -1
        self.nextCourseIndex = 0

        # Thread to wait to join up
        self.wait_thread: Thread = Thread(name='WaitForMeeting', target=self.wait_for_meeting)

        self.time_thread: Thread = Thread(name='CheckTime', target=self.wait_for_time)

        self.time_lock: Lock = Lock()  # Thread lock

        self.joinEvent: Event = Event()
        self.joinThreadIsWaitingEvent: Event = Event()
        self.joinThreadIsWaiting: bool = False
        self.restartEvent: Event = Event()
        self.restartFlag: bool = False
        self.currentCourse: str = ''

    def start(self, account_name: Union[str, None] = None):
        try:
            if not self.account_name:
                self.get_account(account_name)
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
        print("Navigating to course %s", course)
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
        if not self.wait_thread.is_alive():
            self.wait_thread.start()

    def wait_for_meeting(self):
        while True:
            print('Waiting for meeting...')
            while True:
                print('Waiting for join event...')
                self.joinEvent.wait()
                self.time_lock.acquire()
                if self.joinUp:
                    break
                print('Spurious wake-up. Ignoring...')
                self.time_lock.release()
            self.joinEvent.clear()
            print('Join is up! Waiting for AJAX to load...')
            self.driver.implicitly_wait(3)
            self.wait_for_ajax()
            WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, self.JOIN_BTN_ID))).click()
            # three-dot-loader
            WebDriverWait(self.driver, 20).until(ec.invisibility_of_element((By.ID, 'three-dot-loader')))   # What is this for?
            print('Clicked button and stuff...')
            self.joinThreadIsWaiting = True
            self.joinThreadIsWaitingEvent.set()
            self.time_lock.release()
            print('Released time_lock. Waiting for restart flag...')
            # todo: add wait for event to restart
            while True:
                self.restartEvent.wait()
                self.time_lock.acquire()
                if self.restartFlag:
                    break
                self.time_lock.release()
            self.restartFlag = False
            self.time_lock.release()
            print('Restart flag raised. wait_for_meeting is restarting...')

    def wait_for_time(self):
        if len(self.course_schedule) <= 1:
            print('Only one course in list found. Ignoring time scheduling...')
            while True:
                print('Waiting for join thread to need to restart...')
                while True:
                    self.joinThreadIsWaitingEvent.wait()
                    self.time_lock.acquire()
                    if self.joinThreadIsWaiting:
                        break
                    self.time_lock.release()
                print('Restarting join button thread...')
                self.restartFlag = True
                self.restartEvent.set()
                self.joinThreadIsWaiting = False
                self.time_lock.release()
                print('Join button thread restarted from wait_for_time!')
        next_course_time = self.course_schedule[self.nextCourseIndex].start_time
        wait_for_next_day: bool = False
        current_day: int
        while True:
            if wait_for_next_day:
                print(f"Need to wait for next day for course {self.nextCourseIndex}")
                while current_day == datetime.utcnow().weekday():
                    sleep(60)
                wait_for_next_day = False
                print('No longer waiting!')
            now = HourMinute.utcnow()
            if now >= next_course_time : # and now >= self.course_schedule[self.currentCourseIndex].end_time
                print("Time change! Now is %s, and next course time is %s", now, next_course_time)
                print('Trying to acquire time_lock to switch courses')
                self.time_lock.acquire()
                if self.driver.current_url != self.COURSES_URL:
                    if self.driver.current_url == self.LOG_IN_URL:
                        print('Driver was in log-in URL. Logging in...')
                        self.log_in()
                    else:
                        print('Switching to courses URL...')
                        self.driver.get(self.COURSES_URL)
                print('Waiting for webpage to load')
                self.wait_for_ajax()
                self.driver.implicitly_wait(5)
                self.wait_for_ajax()
                print("Done waiting. Navigating to course of %s", self.course_schedule[self.nextCourseIndex].course)
                self.time_lock.release()
                self.navigate_to_course(self.course_schedule[self.nextCourseIndex].course)
                self.time_lock.acquire()
                print("Done navigating. Resetting events")
                self.joinUp = False
                self.joinEvent.clear()
                self.restartFlag = True
                self.restartEvent.set()

                # Setting up next course switch
                self.currentCourseIndex = self.nextCourseIndex
                if self.nextCourseIndex == len(self.course_schedule) - 1:   # Loop the next course
                    self.nextCourseIndex = 0
                    wait_for_next_day = True    # Need to set this because [0] < [current] and likely < now
                    print('Wait for next day set')
                    current_day = datetime.utcnow().weekday()
                else:
                    self.nextCourseIndex += 1
                next_course_time = self.course_schedule[self.nextCourseIndex].start_time
                print("Next course switch to occur at %s", next_course_time)
                print("Releasing time_lock")
                self.time_lock.release()
            else:
                sleep(.5)

    def wait_for_url_change(self):  # Todo
        wait = WebDriverWait(self.driver)
        while True:
            pass

    def get_account(self, name: Union[str, None] = None):
        if name is None:
            self.account_name = input('Enter the account name to use (i.e., the account name in config.json)')
        else:
            self.account_name = name
        if self.account_name not in self.config or 'Email' not in self.config[self.account_name] or 'Password' not in \
                self.config[self.account_name]:
            raise ValueError("Could not find email or password in config file.")

    def wait_for_ajax(self):
        WebDriverWait(self.driver, 20).until(lambda d: self.driver.execute_script("return jQuery.active == 0"))

    def response_interceptor(self, request: Request, response: Response):
        if request.url == self.REQUEST_URL:
            body = response.body.decode()
            if self.joinUp:
                if body[63:67] == 'null':
                    self.joinUp = False
                    # return
            elif body[63:67] != 'null':
                self.joinUp = True
                self.joinEvent.set()
            else:
                file = open("HTTP_req.log", "a")
                file.write(f'-------------\n{datetime.utcnow()}\n'
                           f'Request:\n{request.url}\n{request.body.decode("utf-8")}\n'
                           f'Response:\n{response.body.decode("utf-8")}')
                file.close()
        # Todo: iClicker doesn't auto log-out for at least 1 day. Idk if it'll do further than that though

    def set_up_courses(self):
        for key, value in self.config[self.account_name]['Courses'].items():
            self.course_schedule.append(course_info(HourMinute.from_str(value['Start Time']),
                                                    HourMinute.from_str(value['End Time']), value['Name']))
        self.course_schedule.sort()
        now = HourMinute.utcnow()
        self.nextCourseIndex = len(self.course_schedule)-1
        for i in range(len(self.course_schedule)):
            if now <= self.course_schedule[i]:
                self.nextCourseIndex = i
                break
        if self.nextCourseIndex == 0:
            self.currentCourseIndex = len(self.course_schedule) - 1
        else:
            self.currentCourseIndex = self.nextCourseIndex - 1
        print('Courses set up')
