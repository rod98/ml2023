from fastapi  import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv   import load_dotenv
from wrapped_connection    import WrappedConnection
from model_query_converter import ModelQueryConverter
import uuid
import os

print('Staring in folder:', os.getcwd())

load_dotenv()

class CarModel(BaseModel):
    year        : int   | None
    make        : str   | None
    model       : str   | None
    trim        : str   | None
    body        : str   | None
    transmission: str   | None
    vin         : str   | None
    state       : float | None
    condition   : str   | None
    odometer    : str   | None
    color       : str   | None
    interior    : str   | None
    seller      : str   | None
    mmr         : str   | None
    sellingprice: int   | None

class CarModelWithUUID(CarModel):
    car_id: uuid.UUID

    def __init__(self, uu_id, car):
        super().__init__(car_id=uu_id, **car.model_dump())

class EmptyModel(BaseModel):
    pass


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
    return {"message": "DB initialization"}

@app.get("/car/{car_id}")
async def get_car(car_id: uuid.UUID) -> CarModel | EmptyModel:
    try:
        query = mcq_car_wuuid.select_query(f"car_id = '{car_id}'")

        res = wconn.execute_and_fetch_all(query)[0]
        if not res:
            return EmptyModel()
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    return CarModel.model_validate(res)

@app.put("/car/{car_id}")
async def update_car(car_id: uuid.UUID, car: CarModel) -> CarModel:
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
    return CarModel.model_validate(car)

@app.patch("/car/{car_id}")
async def patch_car(car_id: uuid.UUID, car: dict) -> CarModel:
    try:
        existing_car = await get_car(car_id)
        car_wid = CarModelWithUUID(car_id, existing_car)
        query = mcq_car.update_query(f"car_id = '{car_id}'", list(car_wid.model_dump().keys()))
        d = existing_car.model_dump()
        # d.update(car.dump())
        d.update(car)
        d = CarModel.model_validate(d)
        wconn.executemany(
            query,
            [mcq_car_wuuid.model2list(d)]
        )
    # print(car)
        return d
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.post("/car")
async def add_car(car: CarModel):
    try:
        new_id = uuid.uuid4()
        # print(type(new_id))
        query = mcq_car_wuuid.insert_query()
        uuid_car = CarModelWithUUID(new_id, car)
        wconn.executemany(
            query,
            [mcq_car_wuuid.model2list(uuid_car)]
        )
        # car['uuid'] = new_id
        return uuid_car
    except Exception as e:
        print(e)
        # raise e
        # return {'error': str(e)}
        raise HTTPException(status_code=400, detail=str(e))
