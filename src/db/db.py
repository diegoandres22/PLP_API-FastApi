from sqlalchemy import create_engine
from sqlalchemy.engine import URL 
from sqlalchemy.orm import sessionmaker

url = URL(
    drivername="postgresql",
    username="postgres",
    password="newpassword",
    host="localhost",
    database="postgres",
    port=5432,
    query={}  
)


engine = create_engine(url)
Session = sessionmaker(bind=engine) 
session = Session()