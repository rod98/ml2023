import requests
import uuid

from .base_api_wrapper import BaseApi
import json

class MlApi(BaseApi):
    def get_imp_chars(self):
        return json.loads(requests.get(self.__full_url__('important_characteristics')).text)

    def get_car(self, car_id: uuid.UUID | str, add_smart = False):
        if isinstance(car_id, uuid.UUID):
            car_id = car_id.hex
        params = {}
        if add_smart:
            params['add_smart'] = add_smart
        return json.loads(requests.get(self.__full_url__('car', car_id), params=params).text)

    def search_cars(self, criteria: dict):
        # jc = json.dumps(criteria, indent=4).encode('utf-8')
        # print('Sending:\n', jc)
        response = requests.get(self.__full_url__('car'), json=criteria)
        print('response:', response)
        return json.loads(response.text)

    def find_similar(self, car_id: uuid.UUID | str):
        if isinstance(car_id, uuid.UUID):
            car_id = car_id.hex
        params = {}
        return json.loads(requests.get(self.__full_url__('car', car_id, 'similar'), params=params).text)

    def create_car(self, body: dict):
        print(body)
        return json.loads(requests.post(self.__full_url__('car'), json=body).text)
