from fastapi import FastAPI 
from src.routes.raffle_router import router


app = FastAPI()


app.include_router(router, prefix="/raffle", tags=["Raffle"])