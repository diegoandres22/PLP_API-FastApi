from fastapi import FastAPI 
from src.routes import raffle_router as raffle 
from src.routes import purchase_router as purchase
from src.routes import bank_account_route as bank_account




app = FastAPI()




app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
app.include_router(bank_account.router, prefix="/bank-accounts", tags=["Bank Accounts"])


