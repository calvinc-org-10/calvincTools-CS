from typing import Any
from dataclasses import dataclass

@dataclass
class CallerContext:
    flaskapp:Any = None
    config:Any = None
    app_db:Any = None
    cTools_bind_key:Any = None
    cTools_tablenames:Any = None
    cTools_models:Any = None
