from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def health_check(request):
    return JSONResponse({
        "status": "ok",
        "message": "Service is running"
    })


health_app = Starlette(
    routes=[
        Route("/", endpoint=health_check, methods=["GET"])
    ]
)
