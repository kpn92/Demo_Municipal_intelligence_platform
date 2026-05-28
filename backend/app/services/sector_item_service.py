from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sector_item import SectorItem
from app.schemas.sector_item import SectorItemCreate, SectorItemUpdate


def get_sector_item_by_id(db: Session, item_id: int) -> SectorItem | None:
    statement = select(SectorItem).where(SectorItem.id == item_id)
    return db.execute(statement).scalar_one_or_none()


def get_sector_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sector_id: int | None = None,
    item_type: str | None = None,
    active_only: bool = False,
) -> list[SectorItem]:
    statement = select(SectorItem)

    if sector_id is not None:
        statement = statement.where(SectorItem.sector_id == sector_id)

    if item_type is not None:
        statement = statement.where(SectorItem.item_type == item_type)

    if active_only:
        statement = statement.where(SectorItem.is_active.is_(True))

    statement = statement.order_by(
        SectorItem.sector_id,
        SectorItem.priority,
        SectorItem.id,
    ).offset(skip).limit(limit)

    return list(db.execute(statement).scalars().all())


def create_sector_item(db: Session, item_in: SectorItemCreate) -> SectorItem:
    item = SectorItem(
        sector_id=item_in.sector_id,
        item_type=item_in.item_type,
        name=item_in.name,
        address=item_in.address,
        priority=item_in.priority,
        estimated_minutes=item_in.estimated_minutes,
        latitude=item_in.latitude,
        longitude=item_in.longitude,
        notes=item_in.notes,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_sector_item(
    db: Session,
    item: SectorItem,
    item_in: SectorItemUpdate,
) -> SectorItem:
    update_data = item_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def deactivate_sector_item(db: Session, item: SectorItem) -> SectorItem:
    item.is_active = False
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_sector_item(db: Session, item: SectorItem) -> None:
    db.delete(item)
    db.commit()
