from typing import Any
from dataclasses import dataclass

@dataclass
class CallerContext:
    flaskapp:Any
    config:Any
    app_db:Any
    cTools_bind_key:Any
    cTools_tablenames:Any
    cTools_models:Any
