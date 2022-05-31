from select import select
from fastapi import FastAPI, Response, status, Depends, HTTPException
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from .schemas import PartResponse
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .parts import PARTS
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# , columns: List[str] = ["*"]
@app.get("/parts/{category}/", status_code=status.HTTP_200_OK, response_model=List[PartResponse])
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
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{category} is not a valid part name.")
