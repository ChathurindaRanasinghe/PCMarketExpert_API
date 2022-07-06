from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import text
from .database import Base


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    link = Column(String, nullable=False)
    shop = Column(String, nullable=False)
    availability = Column(Boolean, nullable=False)
    spec = Column(JSON, nullable=False)
    created_date = Column(TIMESTAMP(timezone=True),
                          nullable=False, server_default=text('now()'))

class PcParts(Base):
    __tablename__ = "pc-parts"

    id = Column(Integer, primary_key=True, nullable=False,server_default=text("nextval('products_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    prices = Column(JSON, nullable=False)
    category = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    links = Column(JSON, nullable=False)
    shops = Column(JSON, nullable=False)
    availability = Column(JSON, nullable=False)
    specs = Column(JSON, nullable=False)
    index = Column(Integer, nullable=False)


class ShopMetadata(Base):
    __tablename__ = "shop-basic_data"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    link = Column(String, nullable=False)
    basic_data = Column(JSON, nullable=False)


class Laptops(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True, nullable=False)
    operating_system = Column(String, nullable=False)
    memory = Column(Integer, nullable=False)
    screen = Column(JSON, nullable=False)
    weight = Column(Float, nullable=False)
    storage = Column(JSON, nullable=False)
    cpu = Column(JSON, nullable=False)
    gpu = Column(JSON, nullable=False)
