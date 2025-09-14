from fastapi import FastAPI, Request, HTTPException
from src.routes import raffle_router as raffle 
from src.routes import purchase_router as purchase
from src.routes import bank_account_route as bank_account
from fastapi.middleware.cors import CORSMiddleware
import os

# Leer entorno y whitelist desde variables de entorno
ENVIRONMENT = os.getenv("ENVIRONMENT", "")
WHITELISTED_IPS = os.getenv("WHITELISTED_IPS", "").split(",")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
app.include_router(bank_account.router, prefix="/bank-accounts", tags=["Bank Accounts"])

@app.get("/")
def root():
    return {"message": "Aplicación Patea la Perola iniciada exitosamente"}

