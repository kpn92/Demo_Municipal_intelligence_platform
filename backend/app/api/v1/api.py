from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.cleaning_plan_assignments import router as cleaning_plan_assignments_router
from app.api.v1.collection_history import router as collection_history_router
from app.api.v1.daily_assignments import router as daily_assignments_router
from app.api.v1.employees import router as employees_router
from app.api.v1.fleet import router as fleet_router
from app.api.v1.mapping import router as mapping_router
from app.api.v1.sector_items import router as sector_items_router
from app.api.v1.sectors import router as sectors_router
from app.api.v1.shifts import router as shifts_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(sectors_router)
api_router.include_router(sector_items_router)
api_router.include_router(employees_router)
api_router.include_router(fleet_router)
api_router.include_router(collection_history_router)
api_router.include_router(shifts_router)
api_router.include_router(daily_assignments_router)
api_router.include_router(cleaning_plan_assignments_router)
api_router.include_router(mapping_router)
