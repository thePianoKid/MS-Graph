import requests
import json
import socket
import datetime
import time
from outlook_scraper.slack_scraper import *
import os
from outlook_scraper.query_run import *

unread_messages_request = os.fspath("unread_messages_request.txt")

unread_messages = getUnreadMessages(1,3)

for message in unread_messages:
    local_time_stamp = time.localtime(message["ts"])
    formatted_time_stamp = time.strftime("%A, %B %dth %H:%M",local_time_stamp)
    
    message["ts"] = formatted_time_stamp

messages_package = open(unread_messages, unread_messages_request, mode="w", indent=4)
