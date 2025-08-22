from os import environ
from superset.config import FEATURE_FLAGS as DEFAULT_FEATURE_FLAGS

# SS meta DB
db_user = environ["DB_USER"]
db_pass = environ["DB_PASS"]
db_host = environ["DB_HOST"]
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/postgres"

# SS feature flags
FEATURE_FLAGS = {
    **DEFAULT_FEATURE_FLAGS,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "EMBEDDED_SUPERSET": True,
}

# guest tokens (for embeds)
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_SECRET = environ["GUEST_TOKEN_JWT_SECRET"]
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = int(environ["GUEST_TOKEN_JWT_EXP_SECONDS"])

# CSRF protection
WTF_CSRF_ENABLED = False

# Mapbox
MAPBOX_API_KEY = ""

# cookie settings to make embed easier
SESSION_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SECURE = True # <-- uncomment this when we put SS on HTTPS

# Redis
REDIS_HOST = environ["REDIS_HOST"]
REDIS_PASSWORD = environ["REDIS_PASSWORD"]
redis_url = f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:6380/0"

# Celery (for background tasks e.g. caching with Redis)
BROKER_URL = redis_url
CELERY_RESULT_BACKEND = redis_url
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,
}

# disable validation of Redis cert - it's managed by Azure so it's robust
CELERY_BROKER_TRANSPORT_OPTIONS['ssl'] = {'ssl_cert_reqs': 0}

# allow iframe embeds on the front end and allow loading of our custom JS via script tag
from superset.config import TALISMAN_CONFIG as DEFAULT_TALISMAN_CONFIG
TALISMAN_ENABLED = True
merged_csp = dict(DEFAULT_TALISMAN_CONFIG.get("content_security_policy", {}))
merged_csp["frame-ancestors"] = [
    "'self'",
    "http://localhost:1906",
    "https://stage.hlpst.app",
    "https://hlpst.app",
]
TALISMAN_CONFIG = {
    **DEFAULT_TALISMAN_CONFIG,
    "content_security_policy": merged_csp,
    "frame_options": None,  # Disable X-Frame-Options
}