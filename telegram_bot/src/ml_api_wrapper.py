import json

import requests
import uuid

class MlApi:
    def __init__(self, url, port):
        self.url  = url
        self.port = port

    def __full_url__(self, *args) -> str:
        extra = '/'.join([str(arg) for arg in args])
        return f'http://{self.url}:{self.port}/{extra}'

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
