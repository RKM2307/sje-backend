from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import PumpModel, Brand
from app.models.user import AdminUser
from app.schemas.product import PumpModelOut, PumpModelCreate
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/pump-models", tags=["Pump Models"])

@router.get("", response_model=List[PumpModelOut])
def list_pump_models(
    brand_id: Optional[int] = Query(None),
    pump_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(PumpModel).filter(PumpModel.active == True)
    if brand_id:
        q = q.filter(PumpModel.brand_id == brand_id)
    if pump_type:
        q = q.filter(PumpModel.pump_type.ilike(f"%{pump_type}%"))
    
    models = q.order_by(PumpModel.model_name.asc()).all()
    result = []
    for m in models:
        result.append(PumpModelOut(
            id=m.id,
            brand_id=m.brand_id,
            brand_name=m.brand.name if m.brand else None,
            model_name=m.model_name,
            model_number=m.model_number,
            pump_type=m.pump_type,
            specifications=m.specifications or {},
            active=m.active
        ))
    return result

@router.post("", response_model=PumpModelOut)
def create_pump_model(
    data: PumpModelCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    brand = db.query(Brand).filter(Brand.id == data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=400, detail="Brand not found")

    m = PumpModel(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return PumpModelOut(
        id=m.id,
        brand_id=m.brand_id,
        brand_name=brand.name,
        model_name=m.model_name,
        model_number=m.model_number,
        pump_type=m.pump_type,
        specifications=m.specifications or {},
        active=m.active
    )

@router.put("/{model_id}", response_model=PumpModelOut)
def update_pump_model(
    model_id: int,
    data: PumpModelCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    m = db.query(PumpModel).filter(PumpModel.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Pump model not found")
    for k, v in data.model_dump().items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return PumpModelOut(
        id=m.id,
        brand_id=m.brand_id,
        brand_name=m.brand.name if m.brand else None,
        model_name=m.model_name,
        model_number=m.model_number,
        pump_type=m.pump_type,
        specifications=m.specifications or {},
        active=m.active
    )

@router.delete("/{model_id}")
def delete_pump_model(
    model_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    m = db.query(PumpModel).filter(PumpModel.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Pump model not found")
    db.delete(m)
    db.commit()
    return {"message": "Pump model deleted successfully"}
