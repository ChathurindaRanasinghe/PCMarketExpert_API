

from fastapi import FastAPI, Response, status, Depends, HTTPException, BackgroundTasks, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.api_key import APIKey

from . import models
from .database import engine, get_db, fetch_api_keys, fetch_past_data
from sqlalchemy.orm import Session
from .schemas import PartResponse, ShopMetadataResponse, PcPartResponse, User
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .data import PARTS, SHOPS
from sqlalchemy import INTEGER, Float, Integer, String
from sqlalchemy import cast
from secrets import token_urlsafe
import redis
from .config import settings
import jsonpickle
import hashlib
import datetime
from pprint import pprint

models.Base.metadata.create_all(bind=engine)
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

tags_metadata = [
    {
        "name": "/parts/storage",
        "description": "Filter out storage products based on storage specifications.",
    }
]

app = FastAPI(title="PCMarketExpert", version="0.0.0", openapi_tags=tags_metadata)

def validate_api_key(api_key:str) -> bool:
    hashed_api_key = hashlib.sha256(api_key.encode()).hexdigest()
    api_keys = redis_client.get("api_keys")
    # api_keys = ["2a40a27f06a6b5ee3430f27932b1043ca81490c9f55e0c40936b669bb9c4ffe1"]
    if hashed_api_key in api_keys:
       return True
    else:
       return False 

def get_api_key(api_key_header: str = Security(api_key_header)):
    if validate_api_key(api_key=api_key_header) == True:
        return api_key_header   
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

redis_client = redis.from_url(settings.redis_url,encoding="utf-8", decode_responses=True)


@app.on_event("startup")
async def startup_event(db: Session = Depends(get_db)):
    api_keys = fetch_api_keys()
    redis_client.set("api_keys",jsonpickle.encode(api_keys))
    past_data = fetch_past_data()
    dates = list(past_data.keys())
    for date in dates:
        redis_client.set(date,jsonpickle.encode(past_data[date]))
    
    




@app.get("/")
def root(api_key: APIKey = Depends(get_api_key)):
    return {"hello": "world"}



@app.post("/generate-api-key")
def generate_api_key(user:User,db: Session = Depends(get_db)):
    # validate email
    email_exists = db.query(models.APIKey).filter(models.APIKey.email == user.email).all()
    api_key = None
    if email_exists == []:
        api_key = token_urlsafe(64)
        hashed_api_key = hashed_api_key = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = models.APIKey(email=user.email, api_key=hashed_api_key)
        db.add(api_key_obj)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{user.email} already exists.")

    return api_key


def add_to_cache(key, value):
    redis_client.set(key, jsonpickle.encode(value))


@app.get("/parts/", status_code=status.HTTP_200_OK, response_model=List[PcPartResponse])
def get_parts(
    category: str,
    background_tasks: BackgroundTasks,
    limit: int = 100000,
    db: Session = Depends(get_db),
):
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{limit} is not a valid number of parts.",
        )
    if category in PARTS:
        if category == "storage":
            exists = redis_client.get(f"parts-storage-{limit}")
            if exists == None:
                print("getting from the database")
                parts = (
                    db.query(models.PcParts)
                    .filter(models.PcParts.category == category)
                    .limit(limit)
                    .all()
                )
                if not parts:
                    return Response(status_code=status.HTTP_204_NO_CONTENT)
                background_tasks.add_task(add_to_cache,f"parts-storage-{limit}", parts)
                return parts
            else:
                print("getting from the cache")
                return jsonpickle.decode(exists)
        else:
            parts = (
                    db.query(models.PcParts)
                    .filter(models.PcParts.category == category)
                    .limit(limit)
                    .all()
                )
            
            if not parts:
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            return parts
    elif category not in PARTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{category} is not a valid part name.",
        )


@app.get("/shop/", status_code=status.HTTP_200_OK, response_model=List[PartResponse])
def get_parts_from_shop(
    shop: str, category: str, limit: int = 100000, db: Session = Depends(get_db)
):
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{limit} is not a valid number of parts.",
        )
    if shop in SHOPS and category in PARTS:
        parts = (
            db.query(models.Products)
            .filter(
                models.Products.category == category and models.Products.shop == shop
            )
            .limit(limit)
            .all()
        )
        if not parts:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return parts
    elif shop not in SHOPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{shop} is not a valid shop name.",
        )
    elif category not in PARTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{category} is not a valid part name.",
        )


@app.get(
    "/parts/storage",
    status_code=status.HTTP_200_OK,
    response_model=List[PcPartResponse],
    tags=["/parts/storage"],
)
def get_storage(
    capacity: int | None = None,
    cache: int | None = None,
    type: str | None = None,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{limit} is not a valid number of parts.",
        )
    storage = None
    if capacity is None and cache == None and type == None:
        storage = (
            db.query(models.PcParts).filter(models.PcParts.category == "storage").limit(limit).all()
        )

    elif capacity == None and cache == None and type != None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["type"].astext.cast(String) == type)
            .limit(limit)
            .all()
        )

    elif capacity == None and cache != None and type == None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["cache"].astext.cast(Float) == cache)
            .limit(limit)
            .all()
        )

    elif capacity == None and cache != None and type != None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["cache"].astext.cast(Float) == cache)
            .filter(models.PcParts.specs["type"].astext.cast(String) == type)
            .limit(limit)
            .all()
        )

    elif capacity != None and cache == None and type == None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["capacity"].astext.cast(Float) == capacity)
            .limit(limit)
            .all()
        )

    elif capacity != None and cache == None and type != None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["capacity"].astext.cast(Float) == capacity)
            .filter(models.PcParts.specs["type"].astext.cast(String) == type)
            .limit(limit)
            .all()
        )

    elif capacity != None and cache != None and type == None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["capacity"].astext.cast(Float) == capacity)
            .filter(models.PcParts.specs["cache"].astext.cast(Float) == cache)
            .limit(limit)
            .all()
        )

    elif capacity != None and cache != None and type != None:
        storage = (
            db.query(models.PcParts)
            .filter(models.PcParts.specs["capacity"].astext.cast(Float) == capacity)
            .filter(models.PcParts.specs["cache"].astext.cast(Float) == cache)
            .filter(models.PcParts.specs["type"].astext.cast(String) == type)
            .limit(limit)
            .all()
        )

    if not storage:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return storage

@app.get(
    "/parts/cpu",
    status_code=status.HTTP_200_OK,
    response_model=List[PcPartResponse],
)
def get_cpu(
    core_count: int | None = None,
    tdp: int | None = None,
    integrated_graphics: bool | None = None,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    # print(integrated_graphics)
    cpu = None
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{limit} is not a valid number of parts.",
        )

    else:
        if core_count == None and tdp == None and integrated_graphics == None:
            cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").limit(limit).all()
        )
        elif core_count == None and tdp == None and integrated_graphics != None:
            
            if integrated_graphics == False:
                cpu = (
                db.query(models.PcParts).filter(models.PcParts.category == "cpu").
                filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) == "None").
                limit(limit).all()
                )
            else:
                cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) != "None").
            limit(limit).all()
            )
        elif core_count == None and tdp != None and integrated_graphics == None:
             cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
            limit(limit).all()
            )
        elif core_count == None and tdp != None and integrated_graphics != None:
            
            if integrated_graphics == False:
                cpu = (
                db.query(models.PcParts).filter(models.PcParts.category == "cpu").
                filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) == "None").
                filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
                limit(limit).all()
                )
            else:
                cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) != "None").
            filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
            limit(limit).all()
            )
        elif core_count != None and tdp == None and integrated_graphics == None:
            cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
            limit(limit).all()
            )
        elif core_count != None and tdp == None and integrated_graphics != None:
            if integrated_graphics == False:
                cpu = (
                db.query(models.PcParts).filter(models.PcParts.category == "cpu").
                filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) == "None").
                filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
                limit(limit).all()
                )
            else:
                cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) != "None").
            filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
            limit(limit).all()
            )
        elif core_count != None and tdp != None and integrated_graphics == None:
            cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
            filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
            limit(limit).all()
            )
        elif core_count != None and tdp != None and integrated_graphics != None:
            if integrated_graphics == False:
                cpu = (
                db.query(models.PcParts).filter(models.PcParts.category == "cpu").
                filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) == "None").
                filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
                filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
                limit(limit).all()
                )
            else:
                cpu = (
            db.query(models.PcParts).filter(models.PcParts.category == "cpu").
            filter(models.PcParts.specs["integrated-graphics"].astext.cast(String) != "None").
            filter(models.PcParts.specs["core-count"].astext.cast(Float) == core_count).
            filter(models.PcParts.specs["tdp"].astext.cast(Float) == tdp).
            limit(limit).all()
            )
    return cpu
        


@app.get("/shop-metadata/", status_code=status.HTTP_200_OK, response_model=List[ShopMetadataResponse])
def get_shop_meta_data(db: Session = Depends(get_db)):
    result = []
    PcParts = db.query(models.PcParts).all()
    category_records = db.query(models.PcParts.category).distinct().all()
    categories = []
    for c in category_records:
        categories.append(c[0])
    

    shops = set()
    for part in PcParts:
        distinct_shops = list(part.shops.keys())
        # pprint(list(distinct_shops))
        for shop in distinct_shops:
            shops.add(shop)
    
    for shop in shops:
        shop_response ={
            "shop": shop,
            "numberOfProducts":{},
            "availabilityOfProducts":{}
        }
         
        for c in categories:
            shop_response["numberOfProducts"][c] = 0
            shop_response["availabilityOfProducts"][c] = 0
    
        for part in PcParts:
            distinct_shops = list(part.shops.keys())
            if shop in distinct_shops:
                shop_response["numberOfProducts"][part.category] += 1
                if part.availability[shop] == True:
                    shop_response["availabilityOfProducts"][part.category] += 1
        
        result.append(shop_response)

    return result

@app.get('/past-data/',status_code=status.HTTP_200_OK)
def get_past_data(category:str,date:datetime.date):
    keys = redis_client.keys()
    if category in PARTS:
        key = f"{date}".replace("-","")
        if key in keys:
            return jsonpickle.decode(redis_client.get(key))[category]
        else:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{category} is not valid.")

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
