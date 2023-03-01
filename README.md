# About
This program automatically checks you into an iClicker course. Just keep the program running. You need to have chrome or the chrome webdriver installed.

## Why make this

Because iClicker isn't fun to check-in for attendance. That's it tbh. I can't really justify it beyond this.

Also, I wanted something to try out Selenium on. 

# Requirements

A `config.json` file in the running directory. Should be formatted like this:

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
Course name should be the name exactly as it is in iClicker

# To-do

Implement a way to check for which course to log into.

Maybe have the thing go back and forth based on times?

Implement adjustment of geolocation
