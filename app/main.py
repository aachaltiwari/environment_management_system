from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from contextlib import asynccontextmanager

from app.core.database import connect_mongo, close_mongo
from app.routers.health import health_app
from app.routers.auth import routes as auth_routes


@asynccontextmanager
async def lifespan(app: Starlette):
    # Startup
    await connect_mongo(app)
    yield
    # Shutdown
    await close_mongo(app)


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        *auth_routes,
        Mount("/health", health_app),
        
    ],
)


@app.route("/")
async def root(request):
    return JSONResponse({"message": "Environment Management System"})
