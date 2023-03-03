# About
This program automatically checks you into an iClicker course. Just keep the program running. You need to have Google Chrome or the Chromium WebDriver installed. This is not a script or extension; this opens a webbrowser, logs into iClicker, and waits until the Join Meeting prompt appears.

## Why make this

Because iClicker isn't fun to check-in for attendance. That's it tbh. I can't really justify it beyond this.

Also, I wanted something to try out Selenium on. 

# Requirements

* Python. You can install it [here](https://www.python.org/downloads/).
* Selenium and Selenium-wire python packages. You can install via pip using

  ```
  pip install selenium-wire selenium
  ```
* [Google Chrome](https://www.google.com/chrome/) or the [Chrome WebDriver](https://sites.google.com/chromium.org/driver/) installed.
* A `config.json` file in the running directory. It should be formatted like this:

  ```json
  {
    "Account name":
    {
      "Email": "myemail@email.com",
      "Password": "mypassword123",
      "Course":
        {
        "1": "Course name",
        "2": "Course 2 name"
        }
    }
  }
  ```
    *The `Course name` value should be the name exactly as it is in iClicker*
    
    *Except for `Account name`, no key names should be adjusted*

# Usage

Run the script. You should be prompted for an account name, which should be the `Account name` in the `config.json` (e.g., "Account name" as it is in the above example).

As long as the `config.json` file is set up correctly, it do everything else automatically.

# To-do

* Implement a way to check for which course to log into. Maybe adjust the config file to include a date-time value?
* Maybe have the thing go back and forth based on times?
* Implement adjustment of geolocation.
* Test meetings ending and seeing if the WebDriver needs to restart or press the back arrow to function.
