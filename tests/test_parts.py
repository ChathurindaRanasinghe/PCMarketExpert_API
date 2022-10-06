import json
import pytest
from fastapi import status
from tests.add_test_data import add_test_data
from .test_data import *
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import schemas
from app.database import get_db, Base
from app.config import settings
import requests


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
# add_test_data(database=settings.database_name, password=settings.database_password)

client = TestClient(app)



def test_api_key():
    res = client.post("/generate-api-key",json={"email":"test123@email.com"})
    assert res.status_code == status.HTTP_200_OK



# def test_parts():
#     # print()
#     res = client.get("/parts/", params={'category': 'storage'},headers={"access_token":api_key.content.decode('utf-8')})
#     for index in range(0, len(res.json())):
#         schemas.PcPartResponse(**(res.json()[index]))
#     assert res.status_code == status.HTTP_200_OK


# def test_zero_parts():
#     res = client.get("/parts/", params={'category': 'gpu'})
#     assert res.status_code == status.HTTP_204_NO_CONTENT


# @pytest.mark.parametrize("part", INVALID_PARTS)
# def test_parts_invalid_part(part: str):
#     res = client.get("/parts/", params={'category': f'{part}'})
#     assert res.json()['detail'] == f"{part} is not a valid part name."
#     assert res.status_code == status.HTTP_400_BAD_REQUEST


# @pytest.mark.parametrize("limit", NO_PARTS)
# def test_parts_limit(limit: int):
#     res = client.get("/parts/", params={'category': 'storage', 'limit': f'{limit}'})
#     assert int(limit) >= len(res.json())
#     assert res.status_code == status.HTTP_200_OK


# @pytest.mark.parametrize("limit", NO_PARTS_WITH_MINUS_AND_ZERO)
# def test_parts_limit_with_minus_and_zero(limit: int):
#     res = client.get("/parts/", params={'category': 'storage', 'limit': f'{limit}'})
#     assert res.json()['detail'] == f"{limit} is not a valid number of parts."
#     assert res.status_code == status.HTTP_400_BAD_REQUEST
