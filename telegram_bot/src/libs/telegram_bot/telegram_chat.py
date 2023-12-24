from api_wrappers import MlApi
import json
from model_formatter import ModelFormatter

class TelegramChat:
    def __init__(self, chat_data: dict):
        print('Created new chat with id =', chat_data['id'])
        self.chat_data = chat_data
        self.model_formatter = ModelFormatter(True)

    def _search(self, ml_api: MlApi, msg_text: str):
        print('? Search:')
        lines = msg_text.split('\n')

        criteria = {}
        for line in lines:
            try:
                tokens = line.split()
                if len(tokens) == 2:
                    tokens.append(tokens[-1])

                print(f'?\t{tokens[0]}\t is between {tokens[1]} and {tokens[2]}')
                criteria[tokens[0]] = [tokens[1], tokens[2]]
            except Exception:
                pass

        found = ml_api.search_cars(criteria)

        # print(found)

        # texts = json.loads(found.text)
        texts = found

        if not len(texts):
            texts = ['Ничего не найдено :(']

        for text in texts:
            yield text
            # yield self.model_formatter.format(text)

    def _create(self, ml_api, msg_from, msg_text):
        jdata = {}
        print('+ Create:')
        for line in msg_text.split('\n'):
            if line.strip():
                tokens = line.split()
                jdata[tokens[0]] = tokens[-1]
                print(f'+\t{"{0:35}".format(tokens[0])} = {tokens[-1]}')
        jdata['saledate'] = ""
        jdata['seller'] = '@' + msg_from['username']
        r = ml_api.create_car(jdata)

        # print('~~~~~~~~~~~~~~~~~~')
        # print(r.status_code)
        # print(r.json())
        # print(r.text)
        # print('~~~~~~~~~~~~~~~~~~')

        # return [self.model_formatter.format(r.text)]
        return [r]

    def process_message(self, ml_api: MlApi, msg_from: dict, msg_text: str, msg_entities: dict = {}):
        # for x in msg_text:
        #     yield x
        o = msg_entities[0]['offset']
        l = msg_entities[0]['length']
        msg_text = msg_text[o + l:]

        results = []

        try:
            if msg_entities[0]['text'] == '/search':
                results = self._search(ml_api, msg_text)
            elif msg_entities[0]['text'] == '/create':
                results = self._create(ml_api, msg_from, msg_text)
            elif msg_entities[0]['text'] == '/analyze':
                car_id = msg_text.strip()
                results = [ml_api.get_car(car_id, True)]
            elif msg_entities[0]['text'] == '/get':
                car_id = msg_text.strip()
                results = [ml_api.get_car(car_id, False)]
            elif msg_entities[0]['text'] == '/help':
                t = ml_api.get_imp_chars()
                tt = []
                for k in t.keys():
                    tt.append(f'{"{0:25}".format(k)} {t[k]}')
                results = ['Коэффициенты: <pre>' + '\n'.join(tt) + '</pre>']
            else:
                results = ['Неизвестная комманда!']
        except Exception as e:
            results = [str(e)]

        for text in results:
            yield self.model_formatter.format(text)

