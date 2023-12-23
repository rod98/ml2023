import json

import requests
import uuid

from base_api_wrapper import BaseApi

class MlSmartApi(BaseApi):
    def real_price_indx(self, full_data, our_car):
        url = self.__full_url__('real_price', 0)

        # print('u??', url)

        our_car = our_car.model_dump()
        for field in ['car_id', 'extra_data']:
            if field in our_car:
                del our_car[field]

        data = [our_car]
        data.extend(full_data)

        payload = {
            "data": data
        }

        # print(payload)

        return requests.get(url, json=payload)
