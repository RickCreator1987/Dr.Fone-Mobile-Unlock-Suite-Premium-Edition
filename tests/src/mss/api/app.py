# in src/mss/api/app.py, inside create_app(...)
from mss.api.middleware import RequestContextMiddleware

app.add_middleware(RequestContextMiddleware)