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

class ShopMetadataResponse(BaseModel):
    name: str
    no_of_products: int
    