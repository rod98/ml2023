from fastapi  import FastAPI, HTTPException
from dotenv   import load_dotenv
from wrapped_connection    import WrappedConnection
from ml_smart_api_wrapper  import MlSmartApi
from model_query_converter import ModelQueryConverter
import uuid
import os
import csv
import glob

# import machine_learning.main as mlearn
# from machine_learning.models import CarModel     as TrainingCarModel
# from machine_learning.models import CarModelList as TrainingCarModelList

print('Staring in folder:', os.getcwd())

load_dotenv()

from models import *


smart_api = MlSmartApi(os.getenv('smart_host'), os.getenv('smart_port'))

mcq_car      : ModelQueryConverter = ModelQueryConverter('car_schema.car_table', CarModel)
mcq_car_wuuid: ModelQueryConverter = ModelQueryConverter('car_schema.car_table', CarModelWithUUID)
# mcq_car_wuuid.add_internal_columns({
#     'car_id': 'uuid PRIMARY KEY',
# })

wconn: WrappedConnection = WrappedConnection(
    # 'localhost', 5432,
    # 'car_db', 'car_db_admin', 'car_db_password'
    os.getenv('car_db_host'),
    int(os.getenv('car_db_port')),
    os.getenv('car_db_db'),
    os.getenv('car_db_username'),
    os.getenv('car_db_password'),
)

wconn.connect()

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/init_db")
async def init_db():
    create_query = mcq_car_wuuid.create_query()
    logs = []
    try:
        wconn.executemany(create_query)
    except Exception as e:
        logs.append(e)
        raise HTTPException(400, detail=str(e))
    # try:
    #     wconn.executemany(create_query)
    # except Exception as e:
    #     logs.append(e)

    data_filename_list = glob.glob('data/car_prices*.csv')
    for csv_filename in data_filename_list:
        car_list = []
        with open(csv_filename, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    car = CarModel(**row)
                    new_id = uuid.uuid4()
                    uuid_car = CarModelWithUUID(new_id, **car.model_dump())
                    car_list.append(mcq_car_wuuid.model2list(uuid_car))
                    # wconn.
                except Exception as e:
                    print(e)
                    print(row)

        new_id = uuid.uuid4()
        # print(type(new_id))
        query = mcq_car_wuuid.insert_query()

        wconn.executemany(
            query,
            car_list
        )

    return {"message": "DB initialization"}

async def smart_data_add(*ucars: CarModelWithUUID) -> List[CarModelWithData]:
    for ucar in ucars:
        data = []

        # car = ucar.model_dump()
        # dcar = CarModelWithData(**ucar.model_dump())
        res = smart_api.real_price_indx(data, ucar)
        print(res)

    return ucars

@app.get("/car/{car_id}")
async def get_car(car_id: uuid.UUID) -> CarModel | EmptyModel:
    try:
        query = mcq_car_wuuid.select_query(f"car_id = '{car_id}'")

        res = wconn.execute_and_fetch_all(query)[0]
        print('----', res)
        if not res:
            return EmptyModel()
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    return CarModel.model_validate(res)

@app.get("/car/{car_id}/price")
async def get_price_for_car(car_id: uuid.UUID) -> float:
    raise HTTPException(501)

@app.get("/car")
async def search_cars(search_data: dict) -> list[CarModelWithData]:
    try:
        conditions = []
        cars = []
        train_cars = []
        for search_key in search_data.keys():
            limits = search_data[search_key]
            print(search_key, 'is from', limits[0], 'to', limits[1])
            conditions.append(f'{limits[0]} <= {search_key} AND {search_key} <= {limits[1]}')

        conditions = ' AND '.join(conditions)
        query = mcq_car_wuuid.select_query(conditions)
        res   = wconn.execute_and_fetch_all(query)
        for r in res:
            # raw
            print('----', r)
            cars.append(CarModelWithData.model_validate(r))
            # train_cars.append(CarModel.model_validate(r))

        # car_list = CarModelList(data=train_cars)
        # for idx in range(len(cars)):
        #     r = await mlearn.real_price_indx(car_list, 0)
        #     print('Recommended price:')
        #     print(r)
        #     cars[idx].extra_data['recommended_price'] = r
        return await smart_data_add(*cars)

        # return cars
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.put("/car/{car_id}")
async def update_car(car_id: uuid.UUID, car: CarModel) -> CarModelWithData:
    # car = await get_car(car_id)
    try:
        query = mcq_car.update_query(f"car_id = '{car_id}'")
        wconn.executemany(
            query,
            [mcq_car_wuuid.model2list(car)]
        )
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    # print(car)
    return CarModelWithData.model_validate(car)

@app.patch("/car/{car_id}")
async def patch_car(car_id: uuid.UUID, car: dict) -> CarModelWithData:
    try:
        existing_car = await get_car(car_id)
        car_wid = CarModelWithUUID(car_id, **existing_car.model_dump())
        query = mcq_car.update_query(f"car_id = '{car_id}'", list(car_wid.model_dump().keys()))
        d = existing_car.model_dump()
        # d.update(car.dump())
        d.update(car)
        d = CarModelWithData.model_validate(d)
        wconn.executemany(
            query,
            [mcq_car_wuuid.model2list(d)]
        )
    # print(car)
        return d
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.post("/car")
async def add_car(car: CarModel) -> CarModelWithData:
    try:
        new_id = uuid.uuid4()
        # print(type(new_id))
        query = mcq_car_wuuid.insert_query()
        uuid_car = CarModelWithUUID(new_id, **car.model_dump())

        wconn.executemany(
            query,
            [mcq_car_wuuid.model2list(uuid_car)]
        )
        # car['uuid'] = new_id

        # data_car = CarModelWithData(**uuid_car.model_dump())
        data_car = await smart_data_add(uuid_car)

        return data_car[0]
    except Exception as e:
        print(e)
        # raise e
        # return {'error': str(e)}
        raise HTTPException(status_code=400, detail=str(e))
