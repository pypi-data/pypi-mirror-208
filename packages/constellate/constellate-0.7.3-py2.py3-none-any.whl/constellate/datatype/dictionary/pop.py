from typing import Union, Dict, Any
from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig


# FIXME (prod) this method should not exit - it is standard in python dict
def pop_param_when_available(
    kwargs: Dict = None, key: Any = None, default_value: Any = None
) -> Union[Dict[str, str], SQLAlchemyDBConfig]:
    return kwargs.pop(key, default_value)
