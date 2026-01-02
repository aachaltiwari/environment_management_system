# from starlette.applications import Starlette
# from starlette.routing import Mount
# from contextlib import asynccontextmanager

# from app.core.database import connect_mongo, close_mongo

# from app.graphql.schema import graphql_app
# from app.middlewares.auth import AuthMiddleware


# @asynccontextmanager
# async def lifespan(app: Starlette):
#     # Startup
#     await connect_mongo(app)
#     yield
#     # Shutdown
#     await close_mongo(app)


# app = Starlette(
#     debug=True,
#     lifespan=lifespan,
#     routes=[
#         Mount("/graphql", graphql_app),
        
#     ],
# )


# app.add_middleware(AuthMiddleware)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import connect_mongo, close_mongo
from app.graphql.schema import graphql_app
from app.middlewares.auth import AuthMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_mongo(app)
    yield
    # Shutdown
    await close_mongo(app)


app = FastAPI(
    debug=True,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.mount("/graphql", graphql_app)
