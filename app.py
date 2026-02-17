from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import re

# ─ LINE チャンネルトークン・シークレット ─
LINE_CHANNEL_ACCESS_TOKEN = 'izYoNZ6mcwwHN2dTeXOUgKBcFLd8Ly3k0nULO3jEytUogYsX6+gneQkb26a0LM4rS3cgYypfqI6TOeGUff7u+tyjAZLEtabXx1b0adHOeNbCflZXJw7pz2OaD+WIj1tKDZySb0wrcujtV+f/8p/8NwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'c08cb0360dbddcdb084f61bb88d38a54'
BOT_NAME = "ボット"  # グループで呼ばれるときの名前

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# ─ メモリ（覚えた情報） ─
memory = {}

# ─ 数字計算用関数 ─
def calculate_total(text):
    total = 0
    parts = text.split()
    for p in parts:
        if p.startswith('BB'):
            try:
                n = int(p[2:]) if p[2:] else 1
                total += 60 * n
            except:
                pass
        elif p.startswith('RB'):
            try:
                n = int(p[2:]) if p[2:] else 1
                total += 25 * n
            except:
                pass
        else:
            if re.fullmatch(r'\d+', p):
                total += int(p)
    return total

# ─ LINE Webhook ─
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ─ メッセージイベント ─
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    reply = "わかりません"

    # ─ グループの場合、@ボット名がないと無視 ─
    if event.source.type == "group":
        if not text.startswith(f"@{BOT_NAME}"):
            return
        text = text.replace(f"@{BOT_NAME}", "", 1).strip()

    # ─ 挨拶対応 ─
    greetings = ["こんにちは","おはよう","こんばんは","やあ","お疲れ"]
    if any(g in text for g in greetings):
        reply = f"{text}！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # ─ 覚える ─
    if text.startswith('覚えて！'):
        try:
            key_value = text.replace('覚えて！','').strip()
            key, value = re.split(r'\s+', key_value, maxsplit=1)
            memory[key] = value
            reply = f"{key}を覚えました！"
        except:
            reply = "覚える形式は「覚えて！〇〇 数字」です"

    # ─ 狙い目を返す（部分一致・空白・の無視） ─
    elif '狙い目' in text:
        key = text.replace('狙い目','').replace('の','').replace('　','').replace(' ','').strip()
        found = False
        for mem_key, mem_value in memory.items():
            mem_key_norm = re.sub(r'\s|の','', mem_key)
            if key in mem_key_norm:
                reply = mem_value
                found = True
                break
        if not found:
            reply = f"{key}は覚えていません"

    # ─ 数字計算 ─
    else:
        total = calculate_total(text)
        reply = f"合計は {total} です"

    # ─ 返信 ─
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# ─ ローカルテスト用 ─
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
