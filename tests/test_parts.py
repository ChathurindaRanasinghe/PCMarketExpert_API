from fastapi.testclient import TestClient
from app.main import app
from app import schemas
from fastapi import status
client = TestClient(app)

def test_parts():
    res = client.get("/parts/gpu")
    for index in range(0, len(res.json())):
        schemas.PartResponse(**(res.json()[index]))
    assert res.status_code == status.HTTP_200_OK
    
