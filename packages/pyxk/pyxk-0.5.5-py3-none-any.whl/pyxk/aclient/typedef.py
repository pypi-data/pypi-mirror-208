from typing import (
    Any,
    Union,
    Optional,
    Callable,
)
from multidict import CIMultiDict
from asyncio import AbstractEventLoop

from yarl import URL
from aiohttp import ClientSession, ClientResponse, ClientTimeout


__all__ = ["Session", "EventLoop", "Response", "CIMDict", "StrOrURL", "Timeout", "RequestCallback"]

EventLoop = Optional[AbstractEventLoop]
Session = Optional[ClientSession]
Response = Optional[ClientResponse]
CIMDict = Optional[CIMultiDict]
StrOrURL = Optional[Union[str, URL]]
Timeout = Optional[Union[int, float, ClientTimeout]]
RequestCallback = Callable[[ClientResponse], Any]
