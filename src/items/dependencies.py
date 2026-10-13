"""Items domain dependency aliases."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from db.session import SessionDep
from items.service import ItemService


def get_item_service(session: SessionDep) -> ItemService:
    return ItemService(session)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
