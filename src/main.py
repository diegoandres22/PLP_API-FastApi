from fastapi import FastAPI 
from src.routes import raffle_router as raffle 
from src.routes import purchase_router as purchase


app = FastAPI()


app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
