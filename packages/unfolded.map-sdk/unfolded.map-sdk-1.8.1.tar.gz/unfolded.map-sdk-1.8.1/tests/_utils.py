from copy import deepcopy
from typing import List
from uuid import UUID

from tests.conftest import CommMessage


def check_expected_comm_message(expected: dict, actual: List[CommMessage]):

    new_items = deepcopy(actual)
    for new_item in new_items:
        data = new_item["data"]
        if data["method"] == "custom":
            content = data["content"]
            if "messageId" in content:
                UUID(content["messageId"])
                content.pop("messageId")  # type: ignore

    return any(item.get("data", {}).get("content", {}) == expected for item in new_items)  # type: ignore
