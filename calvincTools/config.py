# proddbtype = "sqlite"
root_path = "."
# root_path = os.path.abspath(os.path.dirname(__file__))
cMenu_dbPath = f"{root_path}\\cMenudb.sqlite"
# cMenu_dbPath = os.path.join(root_path, 'cMenudb.sqlite')

proddbtype = "mysql"
proddbusr = "calvinc461"
proddbpw = "tMJxBC!D4zRpU_2"
proddbsvr = "calvinc461.mysql.pythonanywhere-services.com"
proddbdb = "calvinc461$cMenu"    # calvinc461$default


calvincTools_config = {
    # 'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}:///{cMenu_dbPath}'}
    'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}://{proddbusr}:{proddbpw}@{proddbsvr}/{proddbdb}'}
}
