from typing import TYPE_CHECKING

from garlandtools.models.partials.item_partial import ItemPartial
from garlandtools.models.type import Type

if TYPE_CHECKING:
    from garlandtools.client import Client
    from garlandtools.models.records.base_record import BaseRecord


def partial_factory(partial_data: dict, client: "Client") -> "BaseRecord":  # type: ignore # noqa: E501
    partial_type: Type = Type(partial_data["type"])
    match partial_type:
        case Type.ITEM:
            from garlandtools.models.records.item import Item

            return Item(client=client, partial=ItemPartial(partial_data["obj"]))
        case _:
            # raise ValueError(f"Unknown type {partial_type}")
            print(f"Unknown type {partial_type}")


def record_factory(record_type: Type, record_data: dict, client: "Client"):
    record = record_data[record_type.value]
    related_records = [
        partial_factory(partial, client=client) for partial in record_data["partials"]
    ]
    match record_type:
        case Type.ITEM:
            from garlandtools.models.records.item import Item

            return Item(client, data=record, related_records=related_records)
        case _:
            raise ValueError(f"Unknown type {record_type}")
