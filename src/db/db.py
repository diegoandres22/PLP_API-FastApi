from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")  
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

url = URL(
    drivername="postgresql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
    port=int(DB_PORT),
    query={}
)
engine = create_engine(url)
Session = sessionmaker(bind=engine) 
session = Session()

# from sqlalchemy import create_engine
# from sqlalchemy.engine import URL 
# from sqlalchemy.orm import sessionmaker

# url = URL(
#     drivername="postgresql",
#     username="postgres",
#     password="newpassword",
#     host="localhost",
#     database="postgres",
#     port=5432,
#     query={}  
# )


# engine = create_engine(url)
# Session = sessionmaker(bind=engine) 
# session = Session()