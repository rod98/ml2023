from fastapi import FastAPI
from wrapped_connection import WrappedConnection
from pydantic import BaseModel
from model_query_converter import ModelQueryConverter

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

class CarModelID(CarModel):
    car_id: int

class EmptyModel(BaseModel):
    pass


mcq_car: ModelQueryConverter = ModelQueryConverter('car_schema.car_table', CarModel)
mcq_car.add_internal_columns({
    'car_id': 'SERIAL PRIMARY KEY',
})

wconn: WrappedConnection = WrappedConnection(
    'localhost', 5432,
    'car_db', 'car_db_admin', 'car_db_password'
)

wconn.connect()

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/init_db")
async def init_db():
    create_query = mcq_car.create_query()
    logs = []
    wconn.executemany(create_query)
    # try:
    #     wconn.executemany(create_query)
    # except Exception as e:
    #     logs.append(e)
    return {"message": "hmm", "logs": logs}

@app.get("/car/{car_id}")
async def get_car(car_id: int) -> CarModel | EmptyModel:
    query = mcq_car.select_query(f"car_id = {car_id}")

    res = wconn.execute_and_fetch_all(query)[0]
    if not res:
        return EmptyModel()

    return CarModel.model_validate(res)

@app.put("/car/{car_id}")
async def update_car(car_id: int, car: CarModel) -> CarModel:
    # car = await get_car(car_id)
    query = mcq_car.update_query(f"car_id = {car_id}")
    wconn.executemany(
        query,
        [mcq_car.model2list(car)]
    )
    # print(car)
    return CarModel.model_validate(car)

@app.patch("/car/{car_id}")
async def patch_car(car_id: int, car: dict) -> CarModel:
    existing_car = await get_car(car_id)
    query = mcq_car.update_query(f"car_id = {car_id}", car.keys())
    d = existing_car.model_dump()
    # d.update(car.dump())
    d.update(car)
    d = CarModel.model_validate(d)
    wconn.executemany(
        query,
        [mcq_car.model2list(d)]
    )
    # print(car)
    return d

@app.post("/car")
async def add_car(car: CarModel):
    query = mcq_car.insert_query()
    wconn.executemany(
        query,
        [mcq_car.model2list(car)]
    )
    return car