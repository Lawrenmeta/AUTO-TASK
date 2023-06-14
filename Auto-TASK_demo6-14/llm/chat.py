# encoding:utf-8
import json
import time
import slack
from flask import Flask
from flask_slack import Slack

# userOAuthToken = 'xoxp-5110172238129-5121235539264-5288168885780-5bf2d7849ec7c54301389ed0702ba546'
userOAuthToken = 'xoxp-5110172238129-5121235539264-5393284157810-1106a0125f3ad6bf17a2a84f59eb69b4'
channel_id = 'D05385PNY5P'
name = '你的名字'

app = Flask(__name__)
slack_app = Slack(app)

client = slack.WebClient(token=userOAuthToken)
yesterday = (time.time() - 24 * 60)
yesterday = str(yesterday).split('.')[0]


def chat_with_claude(message):
    print('start chat')
    message = message
    while True:
        # 发送到指定频道
        client.chat_postMessage(channel=channel_id, text=message, as_user=True)

        # 捕获最新的回答
        text = get_history()
        temp = ''
        while True:
            temp = get_history()
            if temp != text and 'Typing' not in temp:
                break
            else:
                time.sleep(1)

        temp = temp.replace('\n\n', '\n')
        # print('Claude:', temp)
        return temp


def get_history():
    history = client.conversations_history(channel=channel_id, oldest=yesterday)
    for human in range(3):
        text1 = history['messages'][human]['text']
        if text1[1] == '&' or text1[1] == '_' or text1[1] == 'O':
            pass
        else:
            break

    # text1 = history['messages'][0]['text']
    # print(text1[0] + ' and ' + text1[1])
    # if text1[1] == '&' or text1[1] == '_' or text1[1] == 'O' :
    #     text1 = history['messages'][1]['text']
    #     print("get history")
    return text1


a = get_history()
print(a)
