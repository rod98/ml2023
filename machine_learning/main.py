from fastapi import FastAPI, HTTPException
from typing import Hashable, Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from models import *
from smart_functions_1 import *
from smart_functions_2 import *

API_PORT: int = 8001

app = FastAPI()


@app.get("/")
async def root():
    """
    root does nothing, just returns hello world
    """
    return {"message": "Hello machine learning"}


@app.get('/show_similar_profitable/{index}')
async def show_similar_profitable_by_id(data: CarModelList, index: int, count: int = 5) -> List[CarModel]:
    """
    show_similar_profitable shows similar and more profitable cars

    :param data: list of CarModel
    :query param index: index from the list above
    :query param count: how many similar cars should be returned
    :return: (by default) five similar and more profitable cars
    """
    # convert from list to DataFrame
    data_converted = pd.DataFrame([vars(el) for el in data.data])

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    prepared_data = prepare_data(data_converted)

    indicies = show_similar_and_more_profitable(prepared_data, index, count)

    # convert from list of dicts to list of CarModel
    cars = [CarModel(**el) for el in data_converted.iloc[indicies].to_dict('records')]
    return cars


@app.get('/car_history/{index}')
async def get_car_history_by_id(data: CarModelList, index: int) -> List[int]:
    """
    get_car_history_by_id returns price history of car by id

    :param data: list of CarModel
    :query param index: index from the list above
    :return: list (200 elements) of price history
    """
    # convert from list to DataFrame
    data_converted = pd.DataFrame([vars(el) for el in data.data])

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    dict_history = assign_history(data_converted)
    car_history = generate_history_for_car(data_converted, dict_history, index, 10.0)

    return car_history


@app.get('/forecast_car_price/{index}')
async def forecast_car_price(data: CarModelList, index: int) -> int:
    """
    forecast_car_price forecsats a car price in the next month

    :param data: list of CarModel
    :query param index: index from the list above
    :return: a car price in the next month
    """
    # convert from list to DataFrame
    data_converted = pd.DataFrame([vars(el) for el in data.data])

    if index < 0 or index >= data_converted.shape[0]:
        raise HTTPException(status_code=422, detail="not valid index")

    dict_history = assign_history(data_converted)
    car_history = generate_history_for_car(data_converted, dict_history, index, 10.0)

    return forecast(car_history)


@app.get('/important_characteristics')
async def important_characteristics(data: CarModelList) -> List[str]:

    data_converted = pd.DataFrame([vars(el) for el in data.data])

    prepared_data = prepare_data(data_converted)

    _, important = important_features(prepared_data)

    return important

@app.get('/real_price/{index}')
async def real_price_indx(data: CarModelList, index: int) -> float:

    data_converted = pd.DataFrame([vars(el) for el in data.data])

    prepared_data = prepare_data(data_converted)

    weights, _ = important_features(prepared_data)

    price = calculate_fair_price_indx(prepared_data, weights, index)

    return price


@app.get('/write_advertisement/{index}')
async def advertisement_indx(data: CarModelList, index: int, price: float = 20000) -> str:

    data_converted = pd.DataFrame([vars(el) for el in data.data])

    prepared_data = prepare_data(data_converted)

    res = write_advertisement_indx(prepared_data, index, price)

    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)

