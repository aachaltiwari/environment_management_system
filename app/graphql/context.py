def get_context_value(request):
    return {
        "request": request,
        "db": request.app.state.db,
        "user": getattr(request.state, "user", None),
    }
