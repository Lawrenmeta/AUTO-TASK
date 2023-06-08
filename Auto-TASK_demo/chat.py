# encoding:utf-8
import json
import time
import slack
from flask import Flask, jsonify
from flask_slack import Slack
from json_fix import fix_json_using_multiple_techniques

userOAuthToken = 'xoxp-5110172238129-5121235539264-5288168885780-5bf2d7849ec7c54301389ed0702ba546'
channel_id = 'D05385PNY5P'
name = '你的名字'

app = Flask(__name__)
slack_app = Slack(app)

client = slack.WebClient(token=userOAuthToken)
yesterday = (time.time() - 24 * 60)
yesterday = str(yesterday).split('.')[0]


def chat_with_claude(message):
    print('sart chat')
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
    text = history['messages'][0]['text']
    if text[1] == '&':
        text = history['messages'][1]['text']
    return text


with open('llm_response_format_1.json') as f:
    data = json.load(f)

data_str = json.dumps(data)
print(data_str)
