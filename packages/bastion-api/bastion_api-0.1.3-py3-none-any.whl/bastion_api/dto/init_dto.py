from typing import List

from pydantic import BaseModel


class BastionServersDto(BaseModel):
    servers_code: List[str] | str = ""
    host: str
    port: int

