from pydantic import BaseModel, RootModel
from typing import List


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