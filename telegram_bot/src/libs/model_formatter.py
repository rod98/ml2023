import json

class ModelFormatter:
    translations = {
        "year": "Год выпуска",
        # "make":
        "model": "Марка",
        # trim: text
        "body": "Корпус",
        "transmission": "Трансмиссия",
        "vin": "VIN",
        "state": "Состояние",
        "condition": "Состояние но другое",
        "odometer": "Километраж",
        "color": "Цвет",
        "interior": "Интерьер",
        "seller": "Продавец",
        # mmr: text
        "sellingprice": "Цена",
        # car_id: a473caca - 449e-461c - a13b - b5219b883d95
    }

    def __translate__(self, key):
        if self.translate:
            return self.translations.get(key, key)
        else:
            return key

    def __init__(self, translate=False):
        self.translate = translate

    def format(self, data: dict | str) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception as e:
                return data

        res = ''
        # res.append('|Характеристика|Значение|')
        # res.append('|--------|-------|')

        if 'car_id' in data:
            res = f'ID Объявления:\n<pre>{data["car_id"]}</pre>\n'

        if 'extra_data' not in data.keys():
            car_state = []
            for key in data.keys():
                key_text = key
                if self.translate:
                    key_text = self.__translate__(key_text)
                key_text  = "{0:35}".format(key_text)
                data_text = data[key]

                if key not in ['seller', 'car_id', 'extra_data']:
                    car_state.append(f'{key_text} {data_text}')

            car_state = '\n'.join(car_state)
            res += 'Характеристики:\n<pre>' + car_state[0:4000] + '</pre>\n'
        else:
            smart_data = []
            data = data['extra_data']
            for key in data.keys():
                key_text = key
                if self.translate:
                    key_text = self.__translate__(key_text)
                key_text  = "{0:35}".format(key_text)
                data_text = data[key]
                smart_data.append(f'{key_text} {data_text}')
            smart_data = '\n'.join(smart_data)
            res += 'Анализ:\n<pre>' + smart_data[0:4000] + '</pre>\n'

        if 'seller' in data:
            res += self.__translate__('seller') + ': ' + data['seller']

        return res
