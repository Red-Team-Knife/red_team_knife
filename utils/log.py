from loguru import logger as l

def debug_route(request):
    l.debug(f"{request.method} {request.path}")
