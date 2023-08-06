from typing import Any, Iterable


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
