import requests
import uuid

class MlApi:
    def __init__(self, url, port):
        self.url  = url
        self.port = port

    def __full_url__(self, *args):
        # if isinstance(extra, list):
        #     extra = '/'.join(extra)
        # extra = ''
        extra = '/'.join([str(arg) for arg in args])
        return f'http://{self.url}:{self.port}/{extra}'

    def get_car(self, car_id: uuid.UUID):
        return requests.get(self.__full_url__('car', car_id.hex))
