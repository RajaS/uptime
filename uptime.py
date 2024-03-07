"""
Check if listed websites are up,
log the status
and send notifications if any website is down

Raja Selvaraj 2024


How to use
----------
List the urls and email recipients in config file
call from cron periodically as `python uptime.py` - maybe every 3 or 5 minutes
when called as `python uptime.py sendmail`, it will also send mail on success - maybe every 24 h
"""

import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import logging
import os
import sys
from datetime import datetime
import json
import time

# load username and password from .env file
# note that separate app password has to be generated in gmail
load_dotenv()
gmail_username = os.getenv("GMAIL_USERNAME")
gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')



def load_config(filename):
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing config file '{filename}'.")
        return None
    

def check_website_uptime(url):
    """
    Given the url
    check if the website is reachable
    returns True/False and message
    """
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = end_time - start_time
            return True, f"Website is up and running. Response time: {response_time:.2f} seconds"
        else:
            return False, f"Website is down with status code: {response.status_code}"
    except requests.ConnectionError:
        return False, "Failed to connect to the website"



def send_alert(contact_id, contact_type, message):
    """
    Send an alert message to a contact
    contact may be any mode of contact
    contact_id is the id and type is the mode
    eg. email address and email
        phone numnber and sms

    Function can be expanded with more modes as required
    """
    if contact_type == "email":
        recipient_email = contact_id
        send_email(recipient_email, message)



def send_email(recipient, message):
    """
    Given the recipient email address and message,
    send an email using a gmail account
    gmail account credentials should be in the dotenv file
    """
    subject = "Email from uptime monitor"
    body = message
    sender = gmail_username
    password = gmail_app_password
    recipients = [recipient]

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        print("Message sent!")

    return 1




def main():
    """
    Check uptime for listed sites
    returns True if all succeed
    if False, return message indicating failure
    """
    # if called with argument "sendmail", will send mail even if all up
    if (len(sys.argv) > 1) and sys.argv[1] == "sendmail":
        SENDMAIL = True
    else:
        SENDMAIL = False
        
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    logfile = open('log.txt', 'a')
    
    config = load_config("config.json")
    if config:
        recipient = config.get("RECIPIENT_EMAIL")
        url_list = config.get("WEBSITE_URLS")
    else:
        return False, "No config file"

    ALL_UP = True
    DOWN_SITES = []
    
    for url in url_list:
        logging.debug("checking website " + url)
        up, msg = check_website_uptime(url)
        if not up:
            logging.debug("website down - " + url)
            ALL_UP = False
            DOWN_SITES.append(url)

    if not ALL_UP:
        # send notification #TODO
        msg = now + ": Not all sites up. Sites down are - " + ",".join(DOWN_SITES)
        logfile.write(msg + '\n')
        logfile.close()
        send_email(recipient, msg)
        return False, msg

    else:
        msg = now + ": All sites up and running - " + ",".join(url_list)
        logfile.write(msg)
        if SENDMAIL:        
            send_email(recipient, msg)

        logfile.close()
        return True, "All sites up"
    


if __name__ == "__main__":
    main()
