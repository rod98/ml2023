import json

import requests
import uuid

from base_api_wrapper import BaseApi
from models import CarModelWithUUID

class MlSmartApi(BaseApi):
    def __init__(self, *args):
        super().__init__(*args)
        self.uuid2idx: dict[uuid.UUID, int] = {}

    def init_data(self, all_data: list[CarModelWithUUID]):
        for idx, data in enumerate(all_data):
            print(data)
            self.uuid2idx[data.car_id] = idx

        payload = {
            'data': [data.model_dump(exclude={'car_id'}) for data in all_data]
        }
        requests.post(self.__full_url__('init_data'), json=payload)


    def real_price_indx(self, car_uuid: uuid.UUID):
        text = '{"ERROR": "Not in UUID - Index match!"}'
        if car_uuid in self.uuid2idx:
            url = self.__full_url__('real_price', self.uuid2idx[car_uuid])

            text = requests.get(url).text
        return text

    def get_car_history_by_id(self, car_uuid: uuid.UUID):
        text = '{"ERROR": "Not in UUID - Index match!"}'
        if car_uuid in self.uuid2idx:
            url = self.__full_url__('car_history', self.uuid2idx[car_uuid])

            text = requests.get(url).text

        return json.loads(text)
