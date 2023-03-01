import seleniumwire.request
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json

requestUrl: str = 'https://api.iclicker.com/student/course/status'
joinUp: bool = False

def wait_for_ajax(driver: webdriver):
    WebDriverWait(driver, 20).until(lambda d: driver.execute_script("return jQuery.active == 0"))

#id is btnJoin
def response_interceptor(request: seleniumwire.request.Request, response: seleniumwire.request.Response):
    if request.url == requestUrl:
        body = response.body.decode()
        global joinUp
        if joinUp:
            if body[63:67] == 'null':
                joinUp = False
        elif body[63:67] != 'null':
            joinUp = True
        else:
            print(body)

accountToUse: str = input('Enter the account name to use (i.e., the account name in config.json)')
with open('config.json', 'r') as f:
    config: dict = json.load(f)
if accountToUse not in config or 'Email' not in config[accountToUse] or 'Password' not in config[accountToUse]:
    raise ValueError("Could not find email or password in config file.")

# Initialize web browser
print("Starting up")
driver: webdriver.Chrome = webdriver.Chrome(
    seleniumwire_options={'exclude_hosts': ['eum-us-west-2.instana.io', 'analytic.rollout.io', 'accounts.google.com',
                                            'www.google-analytics.com',
                                            'iclicker-prod-inst-analytics.macmillanlearning.com'],
                          'ignore_http_methods': ['GET', 'HEAD', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE',
                                                  'PATCH']})

driver.response_interceptor = response_interceptor
print("Initialized")

# Get webpage
driver.get('https://student.iclicker.com/#/login')
print(f"Page title: {driver.title}")

wait_for_ajax(driver)

# Logs in
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'userEmail'))) \
    .send_keys(config[accountToUse]['Email'])
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'userPassword'))) \
    .send_keys(config[accountToUse]['Password'])

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'sign-in-button'))).click()
print('Clicked')
driver.implicitly_wait(3)

# This xpath works
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.XPATH,
                                       f'/html/body/div/div/div/div/div/main/div/ul/li/a[label[text() = '
                                       f'\'{config[accountToUse]["Course"]["3"]}\']]'))).click()
del driver.requests

# required to ensure the program doesn't automatically close
# (this is a chrome specific gimmick; no I don't know how to fix it; i can't get this to work with firefox either)
while True:
    if joinUp:
        wait_for_ajax(driver)
        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'btnJoin')))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'btnJoin'))).click()
    else:
        pass
