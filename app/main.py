from re import T
from fastapi import FastAPI, Response, status, Depends, HTTPException
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from .schemas import PartResponse, LaptopResponse, PcPartResponse
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .data import PARTS, SHOPS
from sqlalchemy import INTEGER, Float, Integer, String
from sqlalchemy import cast

models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "/parts/storage",
        "description": "Filter out storage products based on storage specifications."
    }
]

app = FastAPI(title="PCMarketExpert",version="0.0.0",openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# , columns: List[str] = ["*"]

@app.get("/")
def root():
    return {"message": "===========!DEPLOYMENT SUCCESSFUL!==========="}


@app.get("/parts/", status_code=status.HTTP_200_OK, response_model=List[PartResponse])
def get_parts(category: str, limit: int = 100000, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{limit} is not a valid number of parts.")
    if category in PARTS:
        parts = db.query(models.Products).filter(
            models.Products.category == category).limit(limit).all()
        if not parts:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return parts
    elif category not in PARTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{category} is not a valid part name.")


@app.get("/shop/", status_code=status.HTTP_200_OK, response_model=List[PartResponse])
def get_parts_from_shop(shop: str, category: str, limit: int = 100000, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{limit} is not a valid number of parts.")
    if shop in SHOPS and category in PARTS:
        parts = db.query(models.Products).filter(models.Products.category ==
                                                 category and models.Products.shop == shop).limit(limit).all()
        if not parts:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return parts
    elif shop not in SHOPS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{shop} is not a valid shop name.")
    elif category not in PARTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{category} is not a valid part name.")


@app.get("/parts/storage", status_code=status.HTTP_200_OK, response_model=List[PcPartResponse],tags=["/parts/storage"])
def get_storage(capacity: int | None = None, cache: int | None = None, type: str | None = None, limit: int = 10000, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{limit} is not a valid number of parts.")
    storage = None
    if capacity is None and cache == None and type == None:
        storage = db.query(models.PcParts).filter(models.PcParts.category == "storage").all()

    elif capacity == None and cache == None and type != None:
        storage = db.query(models.PcParts).filter(
            models.PcParts.specs['type'].astext.cast(String) == type).limit(limit).all()

    elif capacity == None and cache != None and type == None:
        storage = db.query(models.PcParts).filter(
            models.PcParts.specs['cache'].astext.cast(Float) == cache).limit(limit).all()

    elif capacity == None and cache != None and type != None:
        storage = db.query(models.PcParts).filter(models.PcParts.specs['cache'].astext.cast(
            Float) == cache).filter(models.PcParts.specs['type'].astext.cast(String) == type).limit(limit).all()

    elif capacity != None and cache == None and type == None:
        storage = db.query(models.PcParts).filter(
            models.PcParts.specs['capacity'].astext.cast(Float) == capacity).limit(limit).all()

    elif capacity != None and cache == None and type != None:
        storage = db.query(models.PcParts).filter(models.PcParts.specs['capacity'].astext.cast(
            Float) == capacity).filter(models.PcParts.specs['type'].astext.cast(String) == type).limit(limit).all()

    elif capacity != None and cache != None and type == None:
        storage = db.query(models.PcParts).filter(models.PcParts.specs['capacity'].astext.cast(
            Float) == capacity).filter(models.PcParts.specs['cache'].astext.cast(Float) == cache).limit(limit).all()

    elif capacity != None and cache != None and type != None:
        storage = db.query(models.PcParts).filter(models.PcParts.specs['capacity'].astext.cast(Float) == capacity).filter(
            models.PcParts.specs['cache'].astext.cast(Float) == cache).filter(models.PcParts.specs['type'].astext.cast(String) == type).limit(limit).all()

    if not storage:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return storage


# """models.Laptops.memory <= memory_max and"""
#  and models.Laptops.weight.between(weight_min, weight_max) ) and
# models.Laptops.storage.between(storage_min,storage_max)


# @app.get("/laptops", status_code=status.HTTP_200_OK, response_model=List[LaptopResponse])
# def get_laptops(storage_type: str | None = None, storage_min: int = 0, storage_max: int = 10000, memory_min: int = 0, memory_max: int = 1000,
#                 operating_system: str | None = None, weight_min: float = 0.0, weight_max: float = 10.0, cpu_brand: str | None = None, cpu_model: str | None = None,
#                 screen_size_min: float = 0.0, screen_size_max: float = 100.0, screen_resolution: str | None = None, screen_refresh_rate_min: int = 0, screen_refresh_rate_max: int = 500,
#                 db: Session = Depends(get_db)):

#     laptops = []
#     if storage_type is not None:
#         laptops = db.query(models.Laptops).filter(models.Laptops.memory.between(memory_min, memory_max))\
#             .filter(models.Laptops.weight.between(weight_min, weight_max))\
#             .filter(models.Laptops.storage[storage_type].astext.cast(Integer).between(storage_min, storage_max))\
#             .all()
#     elif storage_type is None:
#         laptops = db.query(models.Laptops).filter(models.Laptops.memory.between(memory_min, memory_max))\
#             .filter(models.Laptops.weight.between(weight_min, weight_max))\
#             .all()

#     res = []

#     return laptops

    # @app.get("/shop/basic_data",  status_code=status.HTTP_200_OK, response_model=ShopMetadataResponse)
    # def get_shop_metadata(shop: str, db: Session = Depends(get_db)):
    #     if shop in SHOPS:
#         basic_data = db.query)
