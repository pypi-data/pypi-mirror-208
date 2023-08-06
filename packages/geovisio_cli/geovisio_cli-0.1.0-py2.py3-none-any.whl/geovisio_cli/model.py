from dataclasses import dataclass
from typing import Union


@dataclass
class Geovisio:
    url: str
    user: Union[str, None] = None
    password: Union[str, None] = None
