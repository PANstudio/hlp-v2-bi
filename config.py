from os import environ
from superset.config import FEATURE_FLAGS as DEFAULT_FEATURE_FLAGS
from flask_login import current_user
import json

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
    "ENABLE_JAVASCRIPT_CONTROLS": True
}

# guest tokens (for embeds)
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_SECRET = environ["GUEST_TOKEN_JWT_SECRET"]
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = int(environ["GUEST_TOKEN_JWT_EXP_SECONDS"])

# CSRF protection
WTF_CSRF_ENABLED = False

# Mapbox
MAPBOX_API_KEY = environ["MAPBOX_KEY"]

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

# API rate-limiting via Redis
RATELIMIT_STORAGE_URI = redis_url

# disable validation of Redis cert - it's managed by Azure so it's robust
CELERY_BROKER_TRANSPORT_OPTIONS['ssl'] = {'ssl_cert_reqs': 0}

# allow iframe embeds - as well as (reluctantly) `unsafe-eval` - see HLP docs
from superset.config import TALISMAN_CONFIG as DEFAULT_TALISMAN_CONFIG
TALISMAN_ENABLED = True
merged_csp = dict(DEFAULT_TALISMAN_CONFIG.get("content_security_policy", {}))
merged_csp["frame-ancestors"] = [
    "'self'",
    "http://localhost:1906",
    "https://stage.hlpst.app",
    "https://hlpst.app",
]
merged_csp["script-src"] = [
    "'self'",
    "'unsafe-eval'"
]
TALISMAN_CONFIG = {
    **DEFAULT_TALISMAN_CONFIG,
    "content_security_policy": merged_csp,
    "frame_options": None,  # Disable X-Frame-Options
}

# DB re-routing so embeds can dictate which DB to connect to
from db_connection_mutator import db_connection_mutator
DB_CONNECTION_MUTATOR = db_connection_mutator

# Jinja macros to get requested DB and RLS passed in during embed via the `user.username` prop
def jinja_macro(which):
    try:
        user_data = json.loads(current_user.username)
        return user_data.get(which)
    except:
        match which:
            case 'db': return 'default'
            case 'rls': return 'TRUE'

JINJA_CONTEXT_ADDONS = {
    'hlp_db': lambda: jinja_macro('db'),
    'hlp_rls': lambda: jinja_macro('rls')
}