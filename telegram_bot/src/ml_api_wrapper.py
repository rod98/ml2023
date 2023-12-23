import json

import requests
import uuid

from base_api_wrapper import BaseApi

class MlApi(BaseApi):
    def get_car(self, car_id: uuid.UUID):
        return requests.get(self.__full_url__('car', car_id.hex))

    def search_cars(self, criteria: dict):
        # jc = json.dumps(criteria, indent=4).encode('utf-8')
        # print('Sending:\n', jc)
        response = requests.get(self.__full_url__('car'), json=criteria)
        print('response:', response)
        return response

    def create_car(self, body: dict):
        print(body)
        return requests.post(self.__full_url__('car'), json=body)
