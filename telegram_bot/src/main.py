#!/usr/bin/python3

import os
import json
import uuid
import requests

from flask import Flask
from flask import request
from flask import Response
from pyngrok import ngrok, conf
from dotenv  import load_dotenv

from libs.api_wrappers import MlApi

from libs.model_formatter import ModelFormatter

load_dotenv()

telegram_token = os.getenv("tg_token")
api_url  = os.getenv('api_url')
api_port = os.getenv('api_port')
print('telegram token:', telegram_token)

# translator = Translator()
ml_api = MlApi(api_url, api_port)

model_formatter = ModelFormatter(translate=True)

from libs.telegram_bot import TelegramBot


class TunneledApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_tunnel = None
        self.last_msg_id = None

        self.http_tunnel = ngrok.connect('5000', "http")
        print('Ngrok url:', self.http_tunnel.public_url)
        print()

        self.bot = TelegramBot(
            telegram_token,
            self.http_tunnel.public_url,
            ml_api
        )

    def process_message(self, msg: dict):
        print(json.dumps(msg, indent = 4))

        msg_key = ''
        if 'message' in msg:
            msg_key = 'message'
        elif 'edited_message' in msg:
            msg_key = 'edited_message'

        if msg_key:
            msg_text = msg[msg_key].get('text', '')
            msg_from = msg[msg_key].get('from', {})
            msg_chat = msg[msg_key].get('chat', {})
            msg_ents = msg[msg_key].get('entities', {})

            self.bot.process_message(
                msg_chat,
                msg_from,
                msg_text,
                msg_ents
            )

def create_app():
    tele_app = TunneledApp(__name__)
    # app.setup_webhook()

    @tele_app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            msg = request.get_json()

            tele_app.process_message(msg)
        
            return Response('ok', status=200)
        else:
            return "<h1>Welcome!</h1>"
 
    return tele_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
