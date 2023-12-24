import json

import requests
import uuid

class BaseApi:
    def __init__(self, url, port):
        self.url  = url
        self.port = port

    def __full_url__(self, *args) -> str:
        extra = '/'.join([str(arg) for arg in args])
        return f'http://{self.url}:{self.port}/{extra}'
