from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.sector import Sector
from app.schemas.sector import SectorCreate, SectorUpdate


def get_sector_by_id(db: Session, sector_id: int) -> Sector | None:
    statement = select(Sector).where(Sector.id == sector_id)
    return db.execute(statement).scalar_one_or_none()


def get_sector_detail_by_id(db: Session, sector_id: int) -> Sector | None:
    statement = (
        select(Sector)
        .where(Sector.id == sector_id)
        .options(selectinload(Sector.items))
    )
    return db.execute(statement).scalar_one_or_none()


def get_sector_by_code(db: Session, code: str) -> Sector | None:
    statement = select(Sector).where(Sector.code == code)
    return db.execute(statement).scalar_one_or_none()


def get_sectors(db: Session, skip: int = 0, limit: int = 100) -> list[Sector]:
    statement = select(Sector).offset(skip).limit(limit).order_by(Sector.id)
    return list(db.execute(statement).scalars().all())


def create_sector(db: Session, sector_in: SectorCreate) -> Sector:
    sector = Sector(
        code=sector_in.code,
        name=sector_in.name,
        description=sector_in.description,
        is_active=True,
    )
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


def update_sector(db: Session, sector: Sector, sector_in: SectorUpdate) -> Sector:
    update_data = sector_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(sector, field, value)

    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


def deactivate_sector(db: Session, sector: Sector) -> Sector:
    sector.is_active = False
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


def delete_sector(db: Session, sector: Sector) -> None:
    db.delete(sector)
    db.commit()
