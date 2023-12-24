from api_wrappers import MlApi

class TelegramChat:
    def __init__(self, chat_id: int):
        print('Created new chat with id = ', chat_id)
        self.chat_id = chat_id

    def process_message(self, ml_api: MlApi, msg_text: str, msg_entities: dict = {}):
        # for x in msg_text:
        #     yield x
        o = msg_entities[0]['offset']
        l = msg_entities[0]['length']
        msg_text = msg_text[o + l:]

        if msg_entities[0]['text'] == '/search':
            yield msg_text
