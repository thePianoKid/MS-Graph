import logging
import os

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient("xoxb-3495154338565-3500548226500-wBJ4a2qNhk0HbzXZuOnm8zKu")
logger = logging.getLogger(__name__)




group_id = None
bot_name = "slacknotifydemo"
bot_id = "U03EQG46NEQ"

def getUserName(user_email):
    user_obj = client.users_lookupByEmail(email=user_email)
    user_name = user_obj["user"]["name"]
    return user_name

def getUserId(user_email):
    user_obj = client.users_lookupByEmail(email=user_email)
    user_id = user_obj["user"]["id"]
    return user_id



def findConversations(user_name):
    """
    This function returns a list of conversation ids that the user opted in for the Notify service.
    Takes the id of the user and returns a string array contatining conversation ids
    """
    group_id = None
    conversations_ids = []
    try:
    # Call the conversations.list method using the WebClient
        for result in client.conversations_list(types="mpim"):
            if group_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"].count(bot_name)>0 and channel["name"].count(user_name) > 0:
                    conversations_ids.append(channel["id"])
                    #Print result
                    group_id = channel["id"]

    except SlackApiError as e:
        print(f"Error: {e}")

    return conversations_ids

def getConversationHistory(group_id, sinceDays=3):

    day_second_conversion_factor = 86400
    sinceSeconds = sinceDays * day_second_conversion_factor
    current_epoch_time = int(time.time())

    oldest_ts = str(current_epoch_time - sinceSeconds)
    try:
    # Call the conversations.history method using the WebClient
    # conversations.history returns the first 100 messages by default
    # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=group_id, oldest=oldest_ts)

        conversation_history = result["messages"]

        # Print results
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

    return conversation_history



def getUnreadMessages(conversation_history, requesting_user_id):
    unread_messages = []
    

    for i in range(len(conversation_history)):
        if (conversation_history[i]["user"] != requesting_user_id):
            unread_messages.append(conversation_history[i])

    return unread_messages
