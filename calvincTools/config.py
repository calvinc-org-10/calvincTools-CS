from .app_secrets import * # type: ignore

calvincTools_config = {
    'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}:///{cMenu_dbPath}'}
    # 'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}://{proddbusr}:{proddbpw}@{proddbsvr}/{proddbdb}'}
}
