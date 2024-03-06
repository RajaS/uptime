Uptime Monitor
--------------

Why
===
I wanted to be notified immediately if one of my websites was down. 

How
===
Reads a list of websites from a config file. Uses requests library to send a request and check status. If status code is not 200, sends alert by email. Written for my use, comes with no warranty.4

To use
======
1. Copy `.env.example` to `.env` and fill in gmail credentials. Note that app password has to be created. 
2. Copy `config.json.example` to `config.json` and edit the parameters.
3. Set up a cron job to call `python uptime.py` at an interval as you like, maybe 5 minutes.
4. Set up a cron job to call `python uptime.py sendmail` at a longer interval like 24 hours. This sends an email even all is well to inform you that the app is running. 
