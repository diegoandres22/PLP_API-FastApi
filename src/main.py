from fastapi import FastAPI, Request, HTTPException
from src.routes import raffle_router as raffle 
from src.routes import purchase_router as purchase
from src.routes import bank_account_route as bank_account
from fastapi.middleware.cors import CORSMiddleware
import os

# Leer entorno y whitelist desde variables de entorno
ENVIRONMENT = os.getenv("ENVIRONMENT", "")
WHITELISTED_IPS = os.getenv("WHITELISTED_IPS", "").split(",")
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

app = FastAPI()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if ENVIRONMENT == "production" and request.url.scheme != "https":
        raise HTTPException(status_code=403, detail="Usa HTTPS para todas las solicitudes")

    sensitive_methods = ["POST", "PATCH", "PUT"]
    client_host = request.client.host
    if request.method in sensitive_methods and client_host not in WHITELISTED_IPS:
        raise HTTPException(status_code=403, detail="Tu IP no tiene permisos para modificar datos")

    response = await call_next(request)
    return response


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


# from fastapi import FastAPI 
# from src.routes import raffle_router as raffle 
# from src.routes import purchase_router as purchase
# from src.routes import bank_account_route as bank_account
# from fastapi.middleware.cors import CORSMiddleware



# app = FastAPI()

# origins = [
#     "http://localhost:3000",  # front local
#     "https://patealaperola.vercel.app",  # front deployado
#     "https://plpadmin.vercel.app"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # o ["*"] para permitir todos
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
# app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
# app.include_router(bank_account.router, prefix="/bank-accounts", tags=["Bank Accounts"])

# # Ruta de prueba para verificar que la app está corriendo
# @app.get("/")
# def root():
#     return {"message": "Aplicación Patea la Perola iniciada exitosamente"}
