from os import environ
from flask import g
import json

# valid DBs
DBS = ['uk', 'us', 'can', 'aus', 'dev', 'stage']
DB_MAP = {}
for db in DBS:
    DB_MAP[db] = {
        'host': environ[f'DB_{db.upper()}_HOST'],
        'dbname': environ.get(f'DB_{db.upper()}_DB') or 'postgres',
        'user': environ.get(f'DB_{db.upper()}_USER') or 'superset', # defaults to an assumed, read-only user, 'superset'
        'password': environ[f'DB_{db.upper()}_PASS']
    }

# redirect to the DB specified in the JWT claim (embed only)
def db_connection_mutator(sqlalchemy_uri, database, username, security_manager, *args, **kwargs):
    try:
        user_data = json.loads(getattr(g.user, "username", "{}"))
    except:
        print('⚠️ g.user.username is not JSON')
        user_data = {}
    g.db = user_data.get('db') or ''
    g.rls = user_data.get('rls') or 'TRUE'
    print(f"!!! Request to repoint SS to {g.db} DB")
    if g.db in DB_MAP:
        cfg = DB_MAP[g.db]
        sqlalchemy_uri = f"postgresql://{cfg['user']}:{cfg['password']}@{cfg['host']}/{cfg['dbname']}"
    print(f"!!! Repointing SS to {g.db} DB")
    return sqlalchemy_uri, {}