from .telegram_chat  import TelegramChat
from api_wrappers import SimpleTelegramApi
from api_wrappers import MlApi

class TelegramBot:
    def __init__(self, telegram_token, public_url, ml_api: MlApi):
        self.__telapi__ = SimpleTelegramApi(telegram_token)
        self.__telapi__.setup_webhook(public_url)

        self.__ml_api__ = ml_api

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
        r = self.__telapi__.set_commands(commands)

        self.__chats__: dict[int, TelegramChat] = {}

    def process_message(self, msg_chat, msg_from, msg_text, msg_entities = {}):
        print('-------------------------------------')
        print('==== Processing incoming message ====')
        print('- - - - - - - - - - - - - - - - - - -')
        print('From: ', msg_from)
        print('Chat: ', msg_chat)
        print('Text: ', msg_text)

        chat_id = msg_chat['id']

        # if chat_id not in self.__chats__:
        #     self.
        print('Entities: ')
        for entity in msg_entities:
            o = entity['offset']
            l = entity['length']
            entity['text'] = msg_text[o:o + l]
            print('\t', entity['type'], '\t', entity['text'])

        print('\n\n\n')

        if chat_id not in self.__chats__:
            self.__chats__[chat_id] = TelegramChat(msg_chat)

        target_chat = self.__chats__[chat_id]
        responses = target_chat.process_message(
            self.__ml_api__,
            msg_from,
            msg_text,
            msg_entities
        )

        for response in responses:
            self.__telapi__.send_message(
                chat_id,
                response
            )

        print('-------------------------------------')
