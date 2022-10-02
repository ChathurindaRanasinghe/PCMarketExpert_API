from datetime import datetime
from pydantic import BaseModel


class PartResponse(BaseModel):
    id: int
    name: str
    price: int
    category: str
    brand: str
    link: str
    shop: str
    availability: bool
    spec: dict
    created_date: datetime

    class Config:
        orm_mode = True

class User(BaseModel):
    email: str

class PcPartResponse(BaseModel):
    id: int
    name: str
    prices: dict
    category : str 
    brand : str 
    links : dict
    shops : dict
    availability : dict
    specs : dict
    index: int

    

    class Config:
        orm_mode = True

class ShopMetadataResponse(BaseModel):
    shop: str
    numberOfProducts: dict
    availabilityOfProducts: dict

    class Config:
        orm_mode = True


class LaptopResponse(BaseModel):
    id: int
    operating_system: str
    memory: int
    screen: dict
    weight: float
    storage: dict
    cpu: dict
    gpu: dict

    class Config:
        orm_mode = True
# class ShopMetadataResponse(BaseModel):
#     name: str
#     no_of_products: int
