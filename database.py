from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
db_url="postgresql://postgres:Radha%4013@localhost:5432/animesh"
engine=create_engine(db_url)
session= sessionmaker(autocommit=False, autoflush=False, bind=engine)