
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app import schemas
from fastapi import status
<<<<<<< HEAD
import test_data
=======
from .test_data import INVALID_PARTS, NO_PARTS, NO_PARTS_WITH_MINUS_AND_ZERO
>>>>>>> ec49ec3eec3b077010d9157ca079171e5a8baaa7
client = TestClient(app)


def test_parts():
    res = client.get("/parts/gpu")
    for index in range(0, len(res.json())):
        schemas.PartResponse(**(res.json()[index]))
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("part", test_data.INVALID_PARTS)
def test_parts_invalid_part(part: str):
    res = client.get(f"/parts/{part}")
    assert res.json()['detail'] == f"{part} is not a valid part name."
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("limit",  test_data.NO_PARTS)
def test_parts_limit(limit: int):
    res = client.get(f"parts/gpu?limit={limit}")
    assert int(limit) >= len(res.json())
    assert res.status_code == status.HTTP_200_OK

@pytest.mark.parametrize("limit",  test_data.NO_PARTS_WITH_MINUS_AND_ZERO)
def test_parts_limit_with_minus_and_zero(limit: int):
    res = client.get(f"parts/gpu?limit={limit}")
    assert res.json()['detail'] == f"{limit} is not a valid number of parts."
    assert res.status_code == status.HTTP_400_BAD_REQUEST    
