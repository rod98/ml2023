import json

class ModelFormatter:
    def format(self, data: dict | str) -> str:
        if isinstance(data, str):
            data = json.loads(data)

        res = []
        for key in data.keys():
            res.append(f'{key}: {data[key]}')
        res = '\n'.join(res)
        return res
