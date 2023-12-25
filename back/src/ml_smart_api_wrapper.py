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
        self.uuid2idx = {}
        for idx, data in enumerate(all_data):
            # print(data)
            self.uuid2idx[data.car_id] = idx

        payload = {
            'data': [data.model_dump(exclude={'car_id'}) for data in all_data]
        }
        r = requests.post(self.__full_url__('init_data'), json=payload)

        requests.get(self.__full_url__('train_important_characteristics'))
        requests.get(self.__full_url__('train_real_price'))

        return r

    def append_data(self, new_data: list[CarModelWithUUID]):
        # self.uuid2idx = {}

        # for idx, data in enumerate(new_data):
        #     self.uuid2idx[data.car_id] = idx

        payload = {
            'data': [data.model_dump(exclude={'car_id'}) for data in new_data]
        }
        r = requests.post(self.__full_url__('append_data'), json=payload)

        jr = json.loads(r.text)
        # print(jr)
        for idx, data in enumerate(new_data):
            index = jr['indexes'][idx]
            self.uuid2idx[data.car_id] = index
            print(f'New match: {data.car_id} -> {index}')

        # requests.get(self.__full_url__('train_important_characteristics'))
        # requests.get(self.__full_url__('train_real_price'))

        return r


    def real_price_indx(self, car: CarModelWithUUID):
        car_uuid = car.car_id
        text = '{"ERROR": "Not in UUID - Index match!"}'
        if car_uuid in self.uuid2idx:
            url = self.__full_url__('real_price', self.uuid2idx[car_uuid])

            text = requests.get(url).text
        return text

    def forecast_car_price(self, car: CarModelWithUUID):
        car_uuid = car.car_id
        text = '{"ERROR": "Not in UUID - Index match!"}'
        if car_uuid in self.uuid2idx:
            url = self.__full_url__('forecast_car_price', self.uuid2idx[car_uuid])

            text = requests.get(url).text
        return text

    def important_characteristics(self):
        url = self.__full_url__('important_characteristics')
        text = requests.get(url).text

        return json.loads(text)

    def get_car_history_by_id(self, car: CarModelWithUUID):
        car_uuid = car.car_id
        text = '{"ERROR": "Not in UUID - Index match!"}'
        if car_uuid in self.uuid2idx:
            url = self.__full_url__('car_history', self.uuid2idx[car_uuid])

            text = requests.get(url).text

        return json.loads(text)
