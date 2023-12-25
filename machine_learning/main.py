import pandas as pd
from fastapi import FastAPI, HTTPException
from typing import Hashable, Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json

from models import *
from smart_functions_1 import *
from smart_functions_2 import *

API_PORT: int = 8001

app = FastAPI()

# global_data: CarModelList = None
global_data_converted: pd.DataFrame = None

@app.get("/")
async def root():
    """
    root does nothing, just returns hello world
    """
    return {"message": "Hello machine learning"}

@app.post("/init_data")
async def init_data(data: CarModelList):
    #global global_data
    global global_data_converted

    # global_data.data = data.data
    global_data_converted = pd.DataFrame([vars(el) for el in data.data])

    return {
        "status": "ok",
        "db size": len(data.data)
    }

@app.post("/append_data")
async def append_data(data: CarModelList):
    global global_data_converted

    # global_data.data = data.data
    # global_data_converted = pd.DataFrame([vars(el) for el in data.data])
    # data_converted = pd.DataFrame([vars(el) for el in data.data])
    sizes = []
    for el in data.data:
        sizes.append(len(global_data_converted))
        # global_data_converted.append(vars(el))
        global_data_converted.loc[len(global_data_converted)] = vars(el)  # only use with a RangeIndex!

    return {
        "status" : "ok",
        "db size": len(data.data),
        "indexes": sizes
    }


@app.get('/show_similar_profitable/{index}')
async def show_similar_profitable_by_id(index: int, count: int = 5) -> List[CarModel]:
    """
    show_similar_profitable shows similar and more profitable cars

    :param data: list of CarModel
    :query param index: index from the list above
    :query param count: how many similar cars should be returned
    :return: (by default) five similar and more profitable cars
    """
    # convert from list to DataFrame
    data_converted = global_data_converted

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    prepared_data = prepare_data(data_converted)

    indicies = show_similar_and_more_profitable(prepared_data, index, count)

    # convert from list of dicts to list of CarModel
    cars = [CarModel(**el) for el in data_converted.iloc[indicies].to_dict('records')]
    return cars

# global_dict_history = None

@app.get('/car_history/{index}')
async def get_car_history_by_id(index: int) -> List[int]:
    """
    get_car_history_by_id returns price history of car by id

    :param data: list of CarModel
    :query param index: index from the list above
    :return: list (200 elements) of price history
    """

    # convert from list to DataFrame
    data_converted = global_data_converted

    # global global_dict_history
    # if not global_dict_history:
    #     global_dict_history = assign_history(data_converted)
    dict_history = assign_history(data_converted)

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    car_history = generate_history_for_car(data_converted, dict_history, index, 10.0)

    return car_history


@app.get('/forecast_car_price/{index}')
async def forecast_car_price(index: int) -> int:
    """
    forecast_car_price forecsats a car price in the next month

    :param data: list of CarModel
    :query param index: index from the list above
    :return: a car price in the next month
    """
    # convert from list to DataFrame
    data_converted = global_data_converted

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    dict_history = assign_history(data_converted)
    car_history = generate_history_for_car(data_converted, dict_history, index, 10.0)

    return forecast(car_history)


@app.get('/train_important_characteristics')
async def train_important_characteristics():
    important: Dict

    data_converted = global_data_converted

    prepared_data = prepare_data(data_converted)

    _, important = important_features(prepared_data)

    with open(IMP_CHARACS_FILEPATH, 'w+') as json_file:
        json.dump(important, json_file)

    return {"status": 200}


@app.get('/important_characteristics')
async def important_characteristics() -> Dict[str, float]:
    important: Dict

    if not os.path.exists(IMP_CHARACS_FILEPATH) or os.stat(IMP_CHARACS_FILEPATH).st_size == 0:
        raise Exception('call train_important_characteristics before calling important_characteristics')

    with open(IMP_CHARACS_FILEPATH) as json_file:
        important = json.load(json_file)
        #print(important)
        return important


@app.get('/train_real_price')
async def train_real_price():
    if global_data_converted.shape[0] < 10_000:
        raise Exception('too small dataset for training')

    data_converted = global_data_converted[1000:]
    prepared_data, _ = prepare_data2(data_converted)
    train_random_forest(prepared_data)

    return {"status": 200}


@app.get('/real_price/{index}')
async def real_price_indx(index: int) -> float:
    #global dropped_for_index
    data_converted = global_data_converted

    column = data_converted.columns.values

    car_info = dict()
    for i in column:
        car_info[i] = data_converted.iloc[[index]][i].values[0]

    prepared_data, label_encoder = prepare_data2(data_converted)

    price = predict_car_price(prepared_data, label_encoder, car_info)

    return price


@app.get('/write_advertisement/{index}')
async def advertisement_indx(index: int, price: float = 20000.0) -> str:

    data_converted = global_data_converted

    res = write_advertisement_indx(data_converted, index, price)

    return res

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)

