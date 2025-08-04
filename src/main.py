from fastapi import FastAPI 
from src.routes import raffle_router as raffle 
from src.routes import purchase_router as purchase
from typing import Dict




app = FastAPI()




app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])

# @app.post("/")
# async def send_mail() -> Dict:
#     # Cuerpo del mensaje
#     message = EmailMessage()
#     message["From"] = f"Patea la perola <{EMAIL_ADDRESS}>"
#     message["To"] = "diegoandresv22@gmail.com"
#     message["Subject"] = "Gracias por tu compra"
#     message.set_content("<strong>¡Gracias por tu compra, te pertenecen los números 0001 y 2381!</strong>", subtype="html")

#     # Enviar
#     await aiosmtplib.send(
#         message,
#         hostname="smtp.gmail.com",
#         port=587,
#         start_tls=True,
#         username=EMAIL_ADDRESS,
#         password=EMAIL_PASSWORD,
#     )

#     return {"message": "Correo enviado exitosamente"}