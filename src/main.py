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

