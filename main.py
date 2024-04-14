from flask import Flask, request
import requests

app = Flask(__name__)


def send_message(chat_id, text):
    method = "sendMessage"
    token = "7108896576:AAEwiSpVqata0L-H3Sb0tq1d_Fj3MmC34nQ"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


# @app.route("/", methods=["GET", "POST"])
# def receive_update():
#     if request.method == "POST":
#         print(request.json)
#         chat_id = request.json["message"]["chat"]["id"]
#         send_message(chat_id, "pong")
#     return {"ok": True}

@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        print(request.json)
        chat_id = request.json["message"]["chat"]["id"]
        text = request.json["message"]["text"]

        if text == "/help":
            send_message(chat_id, "ХаХаХа")
        else:
            send_message(chat_id, 'pong')

    return {"ok": True}
