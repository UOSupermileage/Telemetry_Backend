from fastapi import FastAPI
from routes.analytics import router as analytics_router
from routes.car import router as car_router
from routes.driver import router as driver_router
from routes.location import router as location_router
from routes.team import router as team_router
from routes.driver_team_history import router as driver_team_history_router
from routes.telemetry import router as telemetry_router

app = FastAPI()

app.include_router(car_router, tags=['Cars'])
app.include_router(driver_router, tags=['Drivers'])
app.include_router(location_router, tags=['Locations'])
app.include_router(team_router, tags=['Teams'])
app.include_router(driver_team_history_router, tags=['Driver History'])
app.include_router(telemetry_router, tags=['Telemetry'])
app.include_router(analytics_router, tags=['Analytics'])