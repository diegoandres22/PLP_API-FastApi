from fastapi import FastAPI 
from src.db.db import session
from src.models.raffleModel import Raffle

app = FastAPI()


@app.post("/newRaffle/")
async def create_raffle_endpoint(
    title: str,
    description: str,
    image: str,
    ticket_price: float,
    min_purchase: float,
    raffle_status: int,
    countdown_time: str,
    progress_percentage: float,
    tickets_account_premium: int,
    state: bool ,
):
    raffle = Raffle(
        title=title,
        description=description,
        image=image,
        ticket_price=ticket_price,
        min_purchase=min_purchase,
        raffle_status=raffle_status,
        countdown_time=countdown_time,
        progress_percentage=progress_percentage,
        tickets_account_premium=tickets_account_premium,
        state=state
    )


    session.add(raffle)
    session.commit()

    return {"Rifa creada": {"id": raffle.id, "title": raffle.title}}

@app.get("/allRaffles/")
async def get_raffles_endpoint():
    raffles = session.query(Raffle).all()
    return {"Rifas": [
        {"id": r.id,
     "title": r.title,
      "description": r.description,
      "image": r.image,
      "ticket_price": r.ticket_price,
      "min_purchase": r.min_purchase,
      "raffle_status": r.raffle_status,
      "countdown_time": r.countdown_time,
      "progress_percentage": r.progress_percentage,
      "tickets_account_premium": r.tickets_account_premium,
      "state": r.state} for r in raffles]
      }

      
@app.get("/raffle/{raffle_id}")
async def get_raffle_endpoint(raffle_id: int):
    raffle = session.query(Raffle).filter(Raffle.id == raffle_id).first()
    if raffle:
        return {
            "id": raffle.id,
            "title": raffle.title,
            "description": raffle.description,
            "image": raffle.image,
            "ticket_price": raffle.ticket_price,
            "min_purchase": raffle.min_purchase,
            "raffle_status": raffle.raffle_status,
            "countdown_time": raffle.countdown_time,
            "progress_percentage": raffle.progress_percentage,
            "tickets_account_premium": raffle.tickets_account_premium,
            "state": raffle.state
        }
    else:
        return {"error": "Rifa no encontrada"}

@app.delete("/raffle/{raffle_id}")
async def delete_raffle_endpoint(raffle_id: int):
    raffle = session.query(Raffle).filter(Raffle.id == raffle_id).first()
    if raffle:
        session.delete(raffle)
        session.commit()
        return {"message": "Rifa eliminada con éxito"}
    else:
        return {"error": "Rifa no encontrada"}

@app.put("/raffle/{raffle_id}")
async def update_raffle_endpoint(  raffle_id: int,
    title: str = None,
    description: str = None,
    image: str = None,
    ticket_price: float = None,
    min_purchase: float = None,
    raffle_status: int = None,
    countdown_time: str = None,
    progress_percentage: float = None,
    tickets_account_premium: int = None,
    state: bool = None
):
    raffle = session.query(Raffle).filter(Raffle.id == raffle_id).first()
    
    if not raffle:
        return {"error": "Rifa no encontrada"}

    if title is not None:
        raffle.title = title
    if description is not None:
        raffle.description = description
    if image is not None:
        raffle.image = image
    if ticket_price is not None:
        raffle.ticket_price = ticket_price
    if min_purchase is not None:
        raffle.min_purchase = min_purchase
    if raffle_status is not None:
        raffle.raffle_status = raffle_status
    if countdown_time is not None:
        raffle.countdown_time = countdown_time
    if progress_percentage is not None:
        raffle.progress_percentage = progress_percentage
    if tickets_account_premium is not None:
        raffle.tickets_account_premium = tickets_account_premium
    if state is not None:
        raffle.state = state

    session.commit()

    return {"message": "Rifa actualizada con éxito", "raffle": {"id": raffle.id, "title": raffle.title}}            