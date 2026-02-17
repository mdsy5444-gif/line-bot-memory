from flask import Flask, request, abort

app = Flask(__name__)

@app.route("/")
def home():
    return "鉄道は動いてます"

@app.route("/callback", methods=["POST"])
def callback():
    # 今はとりあえず受け取ってすぐ返すだけ
    return "OK", 200

if __name__ == "__main__":
    app.run()
