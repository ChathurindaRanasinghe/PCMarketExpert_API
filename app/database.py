import json
from pprint import pprint
from typing import Dict, List, Mapping
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

import psycopg2
from psycopg2.extras import RealDictCursor
import time

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}@"
    f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_api_keys() -> List[str]:

    while True:
        try:
            conn = psycopg2.connect(
                host=settings.database_hostname,
                database=settings.database_name,
                user=settings.database_username,
                password=settings.database_password,
                cursor_factory=RealDictCursor,
            )
            cursor = conn.cursor()
            print("Connection Success! :)")
            break
        except Exception as error:
            print("Connection Failed! :(")
            print("Error: ", error)
            time.sleep(2)
    cursor.execute("""SELECT api_key FROM public."api-keys" """)
    api_key_records = cursor.fetchall()
    api_keys = []
    for row in api_key_records:
        api_keys.append(row["api_key"])

    conn.commit()
    conn.close()

    return api_keys


def fetch_past_data() -> Dict:

    while True:
        try:
            conn = psycopg2.connect(
                host=settings.database_hostname,
                database=settings.database_name,
                user=settings.database_username,
                password=settings.database_password,
                cursor_factory=RealDictCursor,
            )
            cursor = conn.cursor()
            print("Connection Success! :)")
            break
        except Exception as error:
            print("Connection Failed! :(")
            print("Error: ", error)
            time.sleep(2)

    past_data_records = []
    past_data = {}
    for i in range(5, 7):
        past_data[f"2022100{i}"] = {
            "cpu": [],
            "gpu": [],
            "motherboard": [],
            "memory": [],
            "power-supply": [],
            "storage": [],
        }
        cursor.execute(f"""SELECT * FROM public."2022100{i}" """)
        past_data_records.append(cursor.fetchall())

    for i, arr in enumerate(past_data_records):
        for row in arr:
            
            shops = list(row["shops"].keys())
            product = {"name": row["name"], "index": row["index"]}

            for shop in shops:
                product[shop] = {
                    "price": row["prices"][shop],
                    "availability": row["availability"][shop],
                }
            past_data[f"2022100{i+5}"][row["category"]].append(product)
    
    with open("past_data.json","w") as f:
        json.dump(past_data,f)
    return past_data

    # create table names, execute with try and catch, depending on the category and index
