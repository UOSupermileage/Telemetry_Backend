from fastapi import FastAPI
from app.analytics.router import router as analytics_router
from app.cars.router import router as car_router
from app.driver.router import router as driver_router
from app.locations.router import router as location_router
from app.teams.router import router as team_router
from app.driver_history.router import router as driver_team_history_router
from app.telemetry.router import router as telemetry_router

app = FastAPI()

app.include_router(car_router, tags=['Cars'])
app.include_router(driver_router, tags=['Drivers'])
app.include_router(location_router, tags=['Locations'])
app.include_router(team_router, tags=['Teams'])
app.include_router(driver_team_history_router, tags=['Driver History'])
app.include_router(telemetry_router, tags=['Telemetry'])
app.include_router(analytics_router, tags=['Analytics'])