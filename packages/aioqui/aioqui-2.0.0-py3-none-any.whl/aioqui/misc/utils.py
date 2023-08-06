from typing import Any, Optional


async def find(
        where: list[dict[str, Any]],
        key: Any,
        value: Any
) -> tuple[Optional[int], Optional[dict[str, Any]]]:
    for index, item in enumerate(where):
        if item.get(key) == value:
            return index, item
    return None, None
