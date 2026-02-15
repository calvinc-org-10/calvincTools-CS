from calvincTools import app_secrets

calvincTools_config = {
    'SQLALCHEMY_BINDS': {'cToolsdb': app_secrets.cTools_BIND},
}
