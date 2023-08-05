from typing import Any, Iterable
from qasync import asyncSlot


# def asyncwrap(to_call):
#     @asyncSlot()
#     async def wrapped():
#         print(type(to_call))
#         if to_call.__class__.__name__ in ('function', 'method'):
#             await to_call()
#         # elif
#     return wrapped


async def serializable(dictionary: dict[str, Any], exceptions: Iterable[str] = ()) -> dict[str, Any]:
    def validate(value: Any):
        if isinstance(value, bool):
            return True
        elif value is None:
            return False
        elif isinstance(value, str):
            return len(value)

    return {key: value for key, value in dictionary.items() if validate(value) or key in exceptions}


async def find(data: list[dict[str, Any]], key: Any, value: Any) -> tuple[int, dict[str, Any]] | None:
    for index, item in enumerate(data):
        if item.get(key) == value:
            return index, item
