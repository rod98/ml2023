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

    def __init__(self, translate=False):
        self.translate = translate
    def format(self, data: dict | str) -> str:
        if isinstance(data, str):
            data = json.loads(data)

        res = []
        # res.append('|Характеристика|Значение|')
        # res.append('|--------|-------|')
        for key in data.keys():
            key_text = key
            if self.translate:
                key_text = self.translations.get(key, key)
            key_text = "{0:35}".format(key_text)
            res.append(f'{key_text} {data[key]}')
        res = '\n'.join(res)
        res = '<pre>' + res + '</pre>'
        return res
