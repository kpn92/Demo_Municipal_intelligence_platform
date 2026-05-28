from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.shift import Shift
from app.schemas.shift import ShiftCreate, ShiftUpdate


def get_shift_by_id(db: Session, shift_id: int) -> Shift | None:
    statement = select(Shift).where(Shift.id == shift_id)
    return db.execute(statement).scalar_one_or_none()


def get_shift_by_code(db: Session, code: str) -> Shift | None:
    statement = select(Shift).where(Shift.code == code)
    return db.execute(statement).scalar_one_or_none()


def get_shifts(db: Session, skip: int = 0, limit: int = 100) -> list[Shift]:
    statement = select(Shift).offset(skip).limit(limit).order_by(Shift.id)
    return list(db.execute(statement).scalars().all())


def create_shift(db: Session, shift_in: ShiftCreate) -> Shift:
    shift = Shift(
        code=shift_in.code,
        name=shift_in.name,
        start_time=shift_in.start_time,
        end_time=shift_in.end_time,
        is_active=True,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def update_shift(db: Session, shift: Shift, shift_in: ShiftUpdate) -> Shift:
    update_data = shift_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(shift, field, value)

    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def deactivate_shift(db: Session, shift: Shift) -> Shift:
    shift.is_active = False
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def delete_shift(db: Session, shift: Shift) -> None:
    db.delete(shift)
    db.commit()