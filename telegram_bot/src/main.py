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

from ml_api_wrapper import MlApi

# from googletrans import Translator

from telegram_api    import SimpleTelegramApi
from model_formatter import ModelFormatter

# config = configparser.ConfigParser()
# config.read('telegram_bot.ini')
load_dotenv()

telegram_token = os.getenv("tg_token")
api_url  = os.getenv('api_url')
api_port = os.getenv('api_port')
print('telegram token:', telegram_token)

# translator = Translator()
ml_api = MlApi(api_url, api_port)

model_formatter = ModelFormatter(translate=True)

class TunneledApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_tunnel = None
        self.last_msg_id = None
        self.telapi = SimpleTelegramApi(telegram_token)

        # conf.get_default().config_path = "/opt/ngrok/config.yml"

        self.http_tunnel = ngrok.connect('5000', "http")
        self.telapi.setup_webhook(self.http_tunnel.public_url)
        print('Ngrok url:', self.http_tunnel.public_url)
        print()

        commands = [
            {
                'command'    : "search",
                'description': "Поиск машины по заданным параметрам.\nФормат: название_критерия минимум максимум"
            },
            {
                'command'    : "create",
                'description': "Создать новое объявление о продаже машины"
            }
        ]
        r = self.telapi.set_commands(commands)
        print('Command setting status:', r)

    def parse_message(self, message):
        print("message -->", json.dumps(message, indent=4, ensure_ascii=False))

        message_key = 'message'
        if 'edited_message' in message:
            message_key = 'edited_message'

        sjon = {
            'chat_id': message[message_key]['chat']['id'],
            'msg_id':  message[message_key]['message_id'],
            'msg_txt': message[message_key]['text'],
            'author' : message[message_key]['chat']['username']
        }

        return sjon

    def tel_send_message(self, chat_id, text):
        r = self.telapi.send_message(chat_id, text)
        if r.get('ok'):
            self.last_msg_id = r['result']['message_id']

        # print('last_msg_id:', self.last_msg_id)

    def process_message_text(self, chat_id, msg_id, author, text) -> str | list[str] | dict:
        # response = translator.translate(text)

        try:
            tokens = text.split()
            print('tokens:', tokens)
            first_token = tokens[0].lower().lstrip('/')
            if first_token in ['raw_get', 'get', 'rawget']:
                _id = tokens[-1]
                text = ml_api.get_car(uuid.UUID(_id)).text
                text = [model_formatter.format(text)]
            elif first_token in ['search']:
                # tokens = tokens[1:]
                lines = text.split('\n')[1:]

                criteria = {}
                for line in lines:
                    tokens = line.split()
                    if len(tokens) == 2:
                        tokens.append(tokens[-1])

                    print(f'{tokens[0]}\t is between {tokens[1]} and {tokens[2]}')
                    criteria[tokens[0]] = [tokens[1], tokens[2]]

                texts = json.loads(ml_api.search_cars(criteria).text)
                text  = [model_formatter.format(text) for text in texts]

                limit = 3

                if len(text) > limit:
                    text = text[0:limit]
                    text.append('Найдено слишком много машин! Уточните запрос!')

                text = '\n\n\n'.join(text)

                # print('Found:')
                # print(text)
            elif first_token in ['create']:
                # print(author)
                jdata = {}
                for line in text.split('\n')[1:]:
                    tokens = line.split()
                    jdata[tokens[0]] = tokens[-1]
                    print(f'{"{0:35}".format(tokens[0])} = {tokens[-1]}')
                jdata['seller'] = author
                r = ml_api.create_car(jdata)

                print('------------------')
                print(r.status_code)
                print(r.json())
                print(r.text)
                print('------------------')

                if r.status_code != 200:
                    text = r.json()['detail']
                else:
                    text = 'Объявление успешно создано!\nID: <pre>' + json.loads(r.text)["car_id"] + '</pre>'
            else:
                text = '=^.^='
        except Exception as e:
            text = '[ERROR]\n' + str(e)

        return text

    def process_message(self, msg):
        sjson = self.parse_message(msg)
        responses = app.process_message_text(
            sjson['chat_id'],
            sjson['msg_id'],
            sjson['author'],
            sjson['msg_txt'],
        )

        if isinstance(responses, str):
            responses = [responses]

        for resp in responses:
            sr = str(str(resp).encode('UTF-8'))
            print('response:', sr[0:77] + '...' if len(sr) > 80 else sr)
            self.tel_send_message(sjson['chat_id'], resp)

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
