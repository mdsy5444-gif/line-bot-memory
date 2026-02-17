from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import re

app = Flask(__name__)

# 昨日あなたが送ったトークン
LINE_CHANNEL_ACCESS_TOKEN = 'izYoNZ6mcwwHN2dTeXOUgKBcFLd8Ly3k0nULO3jEytUogYsX6+gneQkb26a0LM4rS3cgYypfqI6TOeGUff7u+tyjAZLEtabXx1b0adHOeNbCflZXJw7pz2OaD+WIj1tKDZySb0wrcujtV+f/8p/8NwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'c08cb0360dbddcdb084f61bb88d38a54'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 記憶用辞書
memory = {}

# BB, RBの値
BB_VALUE = 60
RB_VALUE = 25

def calculate_total(text):
    total = 0
    parts = text.split()
    for p in parts:
        if p.startswith('BB'):
            try:
                n = int(p[2:])
                total += n * BB_VALUE
            except:
                pass
        elif p.startswith('RB'):
            try:
                n = int(p[2:])
                total += n * RB_VALUE
            except:
                pass
        else:
            try:
                total += int(p)
            except:
                pass
    return total

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    # 覚える
    if text.startswith('覚えて！'):
        try:
            key_value = text.replace('覚えて！', '').strip()
            key, value = re.split(r'\s+', key_value, maxsplit=1)
            memory[key] = value
            reply = f"{key}を覚えました！"
        except:
            reply = "覚える形式は「覚えて！〇〇 数字」です"
    
    # 狙い目を返す
    elif 'の狙い目' in text:
        key = text.replace('の狙い目', '').strip()
        if key in memory:
            reply = memory[key]
        else:
            reply = f"{key}は覚えていません"
    
    # 数字計算
    else:
        total = calculate_total(text)
        reply = f"合計は {total} です"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(e)
    return 'OK'

if __name__ == "__main__":
    app.run()
