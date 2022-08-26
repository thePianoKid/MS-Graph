from outlook_scraper.slack_scraper import *
import json
import datetime

def packageToJsonString(chats_list):
    unread_messages_json_string = json.dumps(chats_list)
    

    return unread_messages_json_string

user_email = "gabriel.braden@cision.com" #getEmail()
user_name = getUserName(user_email)
user_id = getUserId(user_email)

convs_ids = findConversations(user_name)

chats_list= []
for i in range(len(convs_ids)):
    id = convs_ids[i]
    conv_history = (getConversationHistory(id))
    chats_list.append(getUnreadMessages(conv_history, user_id))

#print(chats_list)
groups = []
message_txt = chats_list[0][0]["text"]

groups =[]
for i in range(len(chats_list)):
    print()
    group_messages =[]
    for j in range(len(chats_list[i])):
        sender_id = chats_list[i][j]["user"]
        sender_name = client.users_info(user=sender_id)["user"]["name"]
        message_txt = chats_list[i][j]["text"]
        time_stamp = chats_list[i][j]["ts"]
        decimalPointIndex = time_stamp.index(".")
        time_stamp = int(time_stamp[0:decimalPointIndex])
        time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d')

        message = {
            "sender": sender_name,
            "text" : message_txt,
            "time_stamp" : time_stamp
        }
        group_messages.append(message)
    groups.append(group_messages)

# json_noisy_string = json.dumps(groups)
# print(json_noisy_string)

def get_groups():
    return groups
