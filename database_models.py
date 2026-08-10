from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Product(Base):    # Define the Product table
    __tablename__ = "product"
    id= Column(Integer, primary_key=True, index=True)
    name= Column(String)
    description= Column(String)
    price= Column(Float)
    quantity= Column(Integer) 

class User(Base):    # Define the User table
    __tablename__ = "users"
    id= Column(Integer, primary_key=True, index=True)
    username= Column(String, unique=True, index=True)
    email= Column(String, unique=True, index=True)
    password_hash= Column(String)