import requests
import json

class SimpleTelegramApi:
    def __init__(self, api_token):
        self.api_token = api_token

    def setup_webhook(self, url):
        telegram_webhook_url = f"https://api.telegram.org/bot{self.api_token}/setWebhook?url={url}"
        requests.get(telegram_webhook_url)

    def send_message(self, chat_id, text):
        url = f'https://api.telegram.org/bot{self.api_token}/sendMessage'

        msg_size_limit = 4096

        results = []

        for i in range(0, len(text), msg_size_limit):
            sub_msg = text[i:i + msg_size_limit]
            payload = {
                'chat_id': chat_id,
                'text'   : sub_msg,
                'parse_mode': 'html'
            }

            r = requests.post(url, json=payload).json()
            results.append(r)

        return results[0]

    def edit_message(self, chat_id, msg_id, text):
        url = f"https://api.telegram.org/bot{self.api_token}/editMessageText" #?chat_id={chat_id}&message_id={msg_id}"
        payload = {
            'chat_id'   : chat_id,
            'message_id': msg_id,
            'text': text
        }
        r = requests.post(url, json=payload).json()
        return r

    def delete_message(self, chat_id, msg_id):
        url = f"https://api.telegram.org/bot{self.api_token}/deleteMessage?chat_id={chat_id}&message_id={msg_id}"
        r = requests.post(url).json()
        return r

    def set_commands(self, commands: list):
        url = f"https://api.telegram.org/bot{self.api_token}/setMyCommands"
        payload = {
            'commands': commands
        }
        r = requests.post(url, json=payload).json()
        return r
