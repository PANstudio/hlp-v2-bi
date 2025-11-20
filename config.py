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
GUEST_ROLE_NAME = "Embed"
GUEST_TOKEN_JWT_SECRET = environ["GUEST_TOKEN_JWT_SECRET"]
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = int(environ["GUEST_TOKEN_JWT_EXP_SECONDS"])

# CSRF protection
WTF_CSRF_ENABLED = False

# Mapbox
MAPBOX_API_KEY = environ["MAPBOX_KEY"]

# cookie settings to make embed easier
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True # <-- not strictly necessary since CF enforces HTTPS anyway

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

# disable fine time grains
TIME_GRAIN_DENYLIST = ['PT1H', 'PT1M', 'PT1S']

# DB connections
SQLALCHEMY_POOL_SIZE = 2
SQLALCHEMY_MAX_OVERFLOW = 1
SQLALCHEMY_POOL_RECYCLE = 1800
SQLALCHEMY_POOL_TIMEOUT = 30

# colours
EXTRA_CATEGORICAL_COLOR_SCHEMES = [{
    'id': 'hlp',
    'description': '',
    'label': 'HLP colours',
    'isDefault': True,
    'colors': ['#ffe05f', '#47beee', '#357174', '#F37660', '#F9BBBA', '#3ABDAF', '#AED9AE']
}]
DEFAULT_CATEGORICAL_COLOR_SCHEME = 'hlp'

# Jinja macros to get bootstrap queries, including all the necessary bits we need in each query...

# ...util - get user data (from guest token)
def get_user_data(which):
    try:
        return json.loads(current_user.username)[which]
    except:
        return False

# ...DB ref to add into SELECT
def db():
    db = get_user_data('db')
    return f"'{db}' AS db" if db else "'default' AS db"

# ...FROM table
def table(alias):
    match(alias):
        case 'im':
            table = 'inbound_messages'
        case 'om':
            table = 'outbound_messages'
        case 'co':
            table = 'conversations'
        case _:
            raise ValueError('Invalid table alias passed to tables()')
    return f'{table} {alias}'

# ...joins - join all the way up the CPSA depending on FROM table. If conversations, join to first inbound message only.
def joins(alias):
    ret = [
        'JOIN agents a ON a.id = co.agent_id',
        'JOIN scripts s ON s.id = a.script_id',
        'JOIN projects p ON p.id = s.project_id',
        'JOIN clients c ON c.id = p.client_id',
    ]
    if alias != 'co':
        ret.insert(0, f'JOIN conversations co ON co.id = {alias}.conversation_id')
    else:
        ret.append(f"""JOIN LATERAL (
          SELECT created_at
          FROM inbound_messages im
          WHERE im.conversation_id = co.id
          ORDER BY created_at ASC
          LIMIT 1
        ) im ON true""")
    return '\n'.join(ret)

# ...where-clause builder
def where(filter_values, from_when=None, to_when=None):
    clauses = [get_user_data('rls') or 'TRUE']
    clauses.append("(co.is_test = CASE WHEN p.status != 'pr' THEN FALSE ELSE TRUE END)")
    tz = "AT TIME ZONE 'utc' AT TIME ZONE p.timezone"
    if from_when:
        clauses.append(f"im.created_at {tz} >= '{from_when}'")
    if to_when:
        clauses.append(f"im.created_at {tz} <= '{to_when}'")
    for fltr in ['medium', 'language']:
        values = filter_values(fltr)
        if values:
            in_part = "'" + "','".join(values) + "'"
            clauses.append(f"co.{fltr} IN ({in_part})")
    return ' AND '.join(clauses)

# ...order by
def order(alias, col='id', dir='DESC'):
    return f'{alias}.{col} {dir}'

# ...declare macros
JINJA_CONTEXT_ADDONS = {
    'db': db,
    'table': table,
    'joins': joins,
    'where': where,
    'order': order
}