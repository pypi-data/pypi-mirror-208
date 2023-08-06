import functools

import orjson
import pydantic
import pydantic.generics


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModel(pydantic.BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        underscore_attrs_are_private = True


parse_raw_as = functools.partial(pydantic.parse_raw_as, json_loads=orjson.loads)
