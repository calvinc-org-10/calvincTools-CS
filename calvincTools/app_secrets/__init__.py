root_path = "."
# root_path = os.path.abspath(os.path.dirname(__file__))
cMenu_dbPath = f"/{root_path}\\appdb.sqlite"

proddbtype = "sqlite"
proddbusr = "db user name"
proddbpw = "db password"
proddbsvr = "db server"
proddbdb = "db name"

cTools_BIND = f'{proddbtype}://{cMenu_dbPath}'
    # 'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}:///{cMenu_dbPath}'}
    # 'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}://{proddbusr}:{proddbpw}@{proddbsvr}/{proddbdb}'}

config_to_use = "development"

sysver_key = 'DEV'

