import asyncio
import warnings
from typing import (
    Any,
    List,
    Tuple,
    Union,
    Optional,
    Mapping,
    Pattern
)
from types import MethodType
from itertools import zip_longest
from multidict import CIMultiDict

import aiohttp

from pyxk.aclient.typedef import (
    StrOrURL,
    Session,
    Response,
    EventLoop,
    CIMDict,
    Timeout,
    RequestCallback
)
from pyxk.utils import (
    chardet,
    LazyLoader,
    get_user_agent,
    default_headers,
)

_yarl = LazyLoader("_yarl", globals(), "yarl")
_selector = LazyLoader("_selector", globals(), "parsel.selector")
aiohttp_client_exceptions = LazyLoader("aiohttp_client_exceptions", globals(), "aiohttp.client_exceptions")

__all__ = ["Client"]



class Client:
    """异步下载器 - 类变量

    :params: limit: aiohttp 并发控制
    :params: timeout: 请求超时时间
    :params: async_sleep: 异步休眠时间
    :params: maximum_retry: 异步请求最大重试次数
    :params: headers: 请求头
    :params: semaphore: asyncio 并发控制
    :params: verify: ssl验证
    :params: start_urls: 请求入口urls
    :params: user_agnet: User-Agent
    :params: aiohttp_kwargs: aiohttp.ClientSession 实例化参数
    :params: retry_status_code: 请求状态码，包含在列表中的进行重新发送
    :params: error_status_code: 请求状态码，包含在列表中直接抛出错误
    :params: until_request_succeed: 请求状态码，知道请求成功为止

    __init__ parameters - 实例化参数

    :params: base_url : base_url
    """

    limit: Optional[int] = None
    timeout: Timeout = None
    async_sleep: Optional[int] = None
    maximum_retry: Optional[int] = None
    headers: Optional[Union[dict, CIMDict]] = None
    semaphore: Optional[int] = None
    verify: Optional[bool] = None
    start_urls: Union[List[str], List[Tuple[str, dict]]] = []
    user_agent: Optional[str] = None
    aiohttp_kwargs: Optional[dict] = None
    retry_status_code: Optional[list] = None
    error_status_code: Optional[list] = None
    until_request_succeed: Optional[Union[bool, List[int]]] = None

    attr = (
        ("limit", 100),
        ("timeout", 7),
        ("headers", CIMultiDict(default_headers())),
        ("semaphore", 16),
        ("verify", True),
        ("async_sleep", 1),
        ("maximum_retry", 20),
        ("user_agent", get_user_agent()),
        ("aiohttp_kwargs", {}),
        ("until_request_succeed", False),
    )

    def __init__(self, *, base_url: StrOrURL=None):
        # event loop
        self._loop: EventLoop = None
        # aiohttp session
        self._session: Session = None
        # base_url
        self._base_url: StrOrURL = self.set_base_url(base_url)

    @classmethod
    def run(cls, **kwargs):
        self = cls(**kwargs)
        # 创建新的 event loop
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # 运行
        self._loop.run_until_complete(self.async_start())
        # 关闭 event loop
        self._loop.close()
        return self

    async def async_start(self) -> None:
        """开启异步下载器"""
        try:
            # event loop
            if (
                not self._loop
                or not isinstance(self._loop, asyncio.AbstractEventLoop)
                or self._loop.is_closed()
            ):
                self._loop = asyncio.get_event_loop()
                asyncio.set_event_loop(self._loop)
            # semaphore
            if not isinstance(self.semaphore, (int, float)) or self.semaphore < 0:
                self.semaphore = dict(self.attr)["semaphore"]
            self.semaphore = asyncio.Semaphore(self.semaphore)
            # aiohttp kwargs
            aiohttp_kwargs = self.aiohttp_kwargs \
                if isinstance(self.aiohttp_kwargs, dict) else dict(self.attr)["aiohttp_kwargs"]
            aiohttp_kwargs = aiohttp_kwargs.copy()
            # timeout
            if not aiohttp_kwargs.__contains__("timeout"):
                if not isinstance(self.timeout, aiohttp.ClientTimeout):
                    timeout = aiohttp.ClientTimeout(
                        total = self.timeout \
                            if isinstance(self.timeout, (int, float)) and self.timeout > 0 else dict(self.attr)["timeout"]
                    )
                else:
                    timeout = self.timeout
                aiohttp_kwargs["timeout"] = timeout
            # connector
            if not aiohttp_kwargs.__contains__("connector"):
                aiohttp_kwargs["connector"] = aiohttp.TCPConnector(
                    loop = self._loop,
                    limit = self.limit \
                        if isinstance(self.limit, int) and self.limit > 0 else dict(self.attr)["limit"],
                    ssl = bool(self.verify) if self.verify is not None else dict(self.attr)["verify"],
                )
            # headers
            if not aiohttp_kwargs.__contains__("headers"):
                headers = CIMultiDict(self.headers) \
                    if isinstance(self.headers, (dict, CIMultiDict)) else dict(self.attr)["headers"]
                headers = headers.copy()
                # User Agent
                if self.user_agent and isinstance(self.user_agent, str):
                    headers["User-Agent"] = self.user_agent
                if not headers.__contains__("User-Agent"):
                    headers["User-Agent"] = dict(self.attr)["user_agent"]
                aiohttp_kwargs["headers"] = headers
            # 创建 aiohttp client_session
            self._session = aiohttp.ClientSession(loop=self._loop, **aiohttp_kwargs)
            # 开始运行
            await self.start()
            result = await self.start_request()
            await self.completed(result)
        finally:
            await self.async_close()

    async def async_close(self):
        """关闭异步下载器"""
        await self.close()
        # 关闭 aiohttp client session
        if isinstance(self._session, aiohttp.ClientSession) and self._session.closed is False:
            await self._session.close()

    async def start_request(self) -> list:
        """发送 start_urls 链接"""
        if not self.start_urls or not isinstance(self.start_urls, (list, tuple)):
            raise NotImplementedError(f"{self.__class__.__name__}.start_urls is not available!")
        tasks = []
        for item in self.start_urls:
            url, cb_kwargs = item, None
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                url, cb_kwargs = item[0], dict(item[1])
            # base_url
            if not self._base_url:
                self.base_url = url
            task = self.request(url=url, callback=self.parse, cb_kwargs=cb_kwargs)
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        return result

    async def request(
        self,
        url: StrOrURL,
        callback: RequestCallback = None,
        *,
        method: str = "GET",
        cb_kwargs: Optional[dict] = None,
        **req_kwargs
    ) -> Union[Response, Any]:
        """异步请求发送以及回调

        :params: url: URL
        :params: callback: 响应response 回调函数(函数是异步的)
        :params: *
        :params: method: 请求方法(default: GET)
        :params: cb_kwargs: 回调函数 关键字参数
        :params: **req_kwargs: 异步请求 request参数
        """
        async with self.semaphore:
            url = self.build_url(url)
            response = await self.send(method=method, url=url, **req_kwargs)
            # 添加自定义方法
            add_method_to_response(response)
            # 开启回调函数
            if callable(callback):
                cb_kwargs = dict(cb_kwargs or {})
                result = await callback(response, **cb_kwargs)
                response.close()
                return result
            return response

    async def send(
        self, method: str, url: StrOrURL, **req_kwargs
    ) -> Response:
        """异步请求发送

        :params: method: 请求方法
        :params: url: URL
        :params: **req_kwargs: 异步请求 request参数
        """
        retry, exc_count = 0, 0
        maximum_retry = self.maximum_retry \
            if isinstance(self.maximum_retry, int) and self.maximum_retry > 0 else dict(self.attr)["maximum_retry"]
        while True:
            try:
                response = await self._session.request(method=method, url=url, **req_kwargs)
                # 抛出 error status_code
                if isinstance(self.error_status_code, (list, tuple)) and response.status in self.error_status_code:
                    raise aiohttp.InvalidURL(f"<Response[{response.status}] {url}>")
                # 重试 retry status_code
                if isinstance(self.retry_status_code, (list, tuple)) and response.status in self.retry_status_code:
                    response.close()
                    retry += 1
                    if retry % 10 == 0:
                        warnings.warn(f"<Response[{response.status}] {url}>, Retry: {retry}", stacklevel=4)
                    await self.sleep()
                    continue
                # 直到请求状态码200才返回 until_request_succeed
                as_succeed = self.until_request_succeed \
                    if self.until_request_succeed is not None else dict(self.attr)["until_request_succeed"]
                if not isinstance(as_succeed, (list, tuple)):
                    as_succeed = [200] if as_succeed else []
                if as_succeed and response.status not in as_succeed:
                    response.close()
                    retry += 1
                    if retry % 10 == 0:
                        warnings.warn(f"<Response[{response.status}] {url}>, Retry: {retry}", stacklevel=4)
                    await self.sleep()
                    continue
                break
            # 请求超时 重试
            except asyncio.exceptions.TimeoutError:
                exc_count += 1
                if exc_count >= maximum_retry:
                    raise
                # warnings.warn(f"<{url}> Timeout", stacklevel=4)
                await self.sleep()
            # 连接错误 重试
            except (
                aiohttp_client_exceptions.ClientOSError,
                aiohttp_client_exceptions.ClientPayloadError,
                aiohttp_client_exceptions.ClientConnectorError,
            ):
                exc_count += 1
                if exc_count >= maximum_retry:
                    raise
                # warnings.warn(f"<{url}> ConnectorError", stacklevel=4)
                await self.sleep()
            # 服务器拒绝连接
            except aiohttp_client_exceptions.ServerDisconnectedError:
                exc_count += 1
                if exc_count >= maximum_retry:
                    raise
                # warnings.warn(f"<{url}> ServerDisconnectedError", stacklevel=4)
                await self.sleep()
        return response

    async def sleep(self, delay: Optional[Union[int, float]]=None, result: Any=None):
        """异步休眠"""
        if not isinstance(delay, int) or delay <= 0:
            delay = self.async_sleep \
                if isinstance(self.async_sleep, int) and self.async_sleep > 0 else dict(self.attr)["async_sleep"]
        return await asyncio.sleep(delay, result=result)

    async def gather(
        self,
        urls: List[StrOrURL],
        callback: RequestCallback = None,
        *,
        method: str = "GET",
        cb_kwargs_list: Optional[List[dict]] = None,
        return_exceptions: bool = False,
        **req_kwargs
    ) -> list:
        """发送url列表，创建异步任务 并发发送

        :params: urls: url list
        :params: callback: 响应response 回调函数(函数是异步的)
        :params: *
        :params: method: 请求方法(default: GET)
        :params: cb_kwargs_list: 回调函数关键字参数列表
        :params: return_exceptions: 错误传递(default: False)
        :params: **req_kwargs: 异步请求 request参数
        """
        # 初始化 cb_kwargs_list
        if isinstance(cb_kwargs_list, dict):
            cb_kwargs_list = [cb_kwargs_list for _ in enumerate(urls)]
        elif isinstance(cb_kwargs_list, (list, tuple)):
            cb_kwargs_list = cb_kwargs_list[:len(urls)]
        else:
            cb_kwargs_list = None
        # 初始化urls
        _urls, _cb_kw, = [], []
        for item in urls:
            url, cb_kwargs = item, None
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                url, cb_kwargs = item[0], dict(item[1])
            _urls.append(url)
            _cb_kw.append(cb_kwargs)
        urls = _urls
        if not cb_kwargs_list:
            cb_kwargs_list = _cb_kw
        del _urls, _cb_kw
        # 收集任务
        tasks = []
        for url, cb_kwargs in zip_longest(urls, cb_kwargs_list):
            task = self.request(
                url=url,
                callback=callback,
                method=method,
                cb_kwargs=cb_kwargs,
                **req_kwargs
            )
            tasks.append(task)
        result = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
        return result

    def build_url(self, _url) -> StrOrURL:
        """构造完整url地址"""
        if not isinstance(_url, (str, _yarl.URL)):
            return _url
        _url = _yarl.URL(_url)
        if _url.is_absolute():
            return _url
        if self._base_url and isinstance(self._base_url, _yarl.URL):
            return self._base_url.join(_url)
        return _url

    @staticmethod
    def set_base_url(url: StrOrURL) -> StrOrURL:
        """设置 base_url"""
        if not url or not isinstance(url, (str, _yarl.URL)):
            return None
        url = _yarl.URL(url)
        if not url.is_absolute():
            # 不是绝对路径
            return None
        return url

    @property
    def loop(self) -> EventLoop:
        """event loop"""
        return self._loop

    @property
    def base_url(self) -> StrOrURL:
        """base_url"""
        return self._base_url

    @base_url.setter
    def base_url(self, _url: StrOrURL) -> None:
        self._base_url = self.set_base_url(_url)

    async def parse(self, response: Response, **kwargs):
        """默认解析函数"""
        raise NotImplementedError(f"'{self.__class__.__name__}.parse' not implemented!")

    async def completed(self, result: list) -> None:
        """运行完成结果回调函数"""

    async def start(self) -> None:
        """创建 aiohttp session 后调用"""

    async def close(self) -> None:
        """关闭 aiohttp session 前调用"""

async def xpath(
    self,
    query: str,
    namespaces: Optional[Mapping[str, str]] = None,
    encoding: Optional[str] = None,
    type: Optional[str] = None,
    root: Optional[Any] = None,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: Optional[bool] = None,
    errors: str = "strict",
    **kwargs
):
    text = await self.text(encoding=encoding, errors=errors)
    selector = _selector.Selector(
        text=text,
        type=type,
        _expr=_expr,
        namespaces=namespaces,
        root=root,
        base_url=base_url,
        huge_tree=_selector.LXML_SUPPORTS_HUGE_TREE if huge_tree is None else huge_tree,
    )
    return selector.xpath(query=query, **kwargs)

async def css(
    self,
    query: str,
    namespaces: Optional[Mapping[str, str]] = None,
    encoding: Optional[str] = None,
    type: Optional[str] = None,
    root: Optional[Any] = None,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: Optional[bool] = None,
    errors: str = "strict"
):
    text = await self.text(encoding=encoding, errors=errors)
    selector = _selector.Selector(
        text=text,
        type=type,
        _expr=_expr,
        namespaces=namespaces,
        root=root,
        base_url=base_url,
        huge_tree=_selector.LXML_SUPPORTS_HUGE_TREE if huge_tree is None else huge_tree,
    )
    return selector.css(query=query)

async def re(
    self,
    regex: Union[str, Pattern[str]],
    replace_entities: bool = True,
    namespaces: Optional[Mapping[str, str]] = None,
    encoding: Optional[str] = None,
    type: Optional[str] = None,
    root: Optional[Any] = None,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: Optional[bool] = None,
    errors: str = "strict",
):
    text = await self.text(encoding=encoding, errors=errors)
    selector = _selector.Selector(
        text=text,
        type=type,
        _expr=_expr,
        namespaces=namespaces,
        root=root,
        base_url=base_url,
        huge_tree=_selector.LXML_SUPPORTS_HUGE_TREE if huge_tree is None else huge_tree,
    )
    return selector.re(regex=regex, replace_entities=replace_entities)

def urljoin(self, _url):
    if isinstance(_url, str):
        _url = _yarl.URL(_url)
    elif not isinstance(_url, _yarl.URL):
        return _url
    if _url.is_absolute():
        return _url
    return self.url.join(_url)

async def apparent_encoding(self):
    byte = await self.read()
    return chardet(byte)["encoding"]

def add_method_to_response(response):
    """为异步response添加实例方法"""
    response.re = MethodType(re, response)
    response.css = MethodType(css, response)
    response.xpath = MethodType(xpath, response)
    response.urljoin = MethodType(urljoin, response)
    response.apparent_encoding = MethodType(apparent_encoding, response)
