from .app_secrets import * #pylint: disable=wildcard-import, unused-wildcard-import

calvincTools_config = {
    'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}:///{cMenu_dbPath}'}
    # 'SQLALCHEMY_BINDS': {'cToolsdb': f'{proddbtype}://{proddbusr}:{proddbpw}@{proddbsvr}/{proddbdb}'}
}
