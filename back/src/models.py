from pydantic import BaseModel
from typing import List
from typing import Optional
import uuid

class CarModel(BaseModel):
    year        : int
    make        : str
    model       : str
    trim        : str
    body        : str
    transmission: str
    vin         : str
    state       : str
    condition   : float
    odometer    : float
    color       : str
    interior    : str
    seller      : str
    mmr         : int
    sellingprice: int
    saledate    : str

class CarModelList(BaseModel):
    data: List[CarModel]

class CarModelWithUUID(CarModel):
    car_id: uuid.UUID

    def __init__(self, car_id, **kwargs):
        super().__init__(car_id=car_id, **kwargs)

class CarModelWithData(CarModelWithUUID):
    extra_data: Optional[dict] = {}

class EmptyModel(BaseModel):
    pass