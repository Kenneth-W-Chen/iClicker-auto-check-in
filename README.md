# About
This program automatically checks you into an iClicker course. Just keep the program running. You need to have chrome or the chrome webdriver installed.

## Why make this

Because iClicker isn't fun to check-in for attendance. I've had too many professors who were just too lazy to learn our names (e.g., we had less than 15 people) and just take attendance on their own.

Like, if iClicker is for quizzes and stuff, then by all means do it. But if you're using it as a glorified attendance software, maybe consider using something without 30 requests to various analytics hosts. And don't check the location.

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
