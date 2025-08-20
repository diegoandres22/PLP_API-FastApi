from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.services import raffle_service
from src.schemas.raffle_schema import RaffleCreate, RaffleUpdate
from uuid import UUID
from datetime import datetime
from src.services.gcs_service import upload_file_to_gcs


router = APIRouter()

@router.get("/all/")
def get_all_raffles(db: Session = Depends(get_db)):
    return raffle_service.get_raffles_endpoint(db)

@router.post("/new/")
async def create_raffle_endpoint(
    title: str = Form(...),
    description: str = Form(...),
    ticket_price: float = Form(...),
    min_purchase: float = Form(...),
    raffle_status: int = Form(...),
    state: bool = Form(...),
    trophy: str = Form(...),
    secondPrize: str = Form(...),
    additionalPrize: str = Form(...),
    premium_ticket1: int = Form(None),
    premium_ticket2: int = Form(None),
    premium_ticket3: int = Form(None),
    premium_ticket4: int = Form(None),
    premium_ticket5: int = Form(None),
    premium_ticket6: int = Form(None),
    total_tickets: int = Form(...),
    lottery_date: datetime = Form(...),
    created_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_bytes = await file.read()
    image_url = upload_file_to_gcs(file_bytes, file.filename)

    raffle_data = RaffleCreate(
        title=title,
        description=description,
        ticket_price=ticket_price,
        min_purchase=min_purchase,
        raffle_status=raffle_status,
        state=state,
        trophy=trophy,
        secondPrize=secondPrize,
        additionalPrize=additionalPrize,
        premium_ticket1=premium_ticket1,
        premium_ticket2=premium_ticket2,
        premium_ticket3=premium_ticket3,
        premium_ticket4=premium_ticket4,
        premium_ticket5=premium_ticket5,
        premium_ticket6=premium_ticket6,
        total_tickets=total_tickets,
        lottery_date=lottery_date,
        created_by=created_by
    )

    return raffle_service.create_raffle(raffle_data, db, image_url)
# @router.post("/new/")
# async def create_raffle_endpoint(
#     data: RaffleCreate,
#     db: Session = Depends(get_db)
# ):
#     return raffle_service.create_raffle(data, db)

@router.get("/{raffle_id}")
def get_raffle_by_id(raffle_id: UUID, db: Session = Depends(get_db)):
    return raffle_service.get_raffle_by_id_endpoint(db, raffle_id)

@router.delete("/{raffle_id}")
def delete_raffle(raffle_id: UUID, db: Session = Depends(get_db)):
    return raffle_service.delete_raffle_endpoint(db, raffle_id)

@router.put("/{raffle_id}")
def update_raffle(
    raffle_id: UUID,
    data: RaffleUpdate,
    db: Session = Depends(get_db)
):
    return raffle_service.update_raffle_endpoint(db, raffle_id, data)