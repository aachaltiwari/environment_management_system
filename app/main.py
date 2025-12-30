from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from contextlib import asynccontextmanager

from app.core.database import connect_mongo, close_mongo
from app.routers.health import health_app

from ariadne.asgi import GraphQL
from app.graphql.schema import schema
from app.graphql.context import get_context_value
from app.middlewares.auth import AuthMiddleware


@asynccontextmanager
async def lifespan(app: Starlette):
    # Startup
    await connect_mongo(app)
    yield
    # Shutdown
    await close_mongo(app)


graphql_app = GraphQL(
    schema,
    context_value=get_context_value,
    debug=True, 
)


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Mount("/health", health_app), 
        Mount("/graphql", graphql_app),
        
    ],
)

@app.route("/")
async def root(request):
    return JSONResponse({"message": "Environment Management System"})


app.add_middleware(AuthMiddleware)





