import os
import time
import warnings
from urllib.parse import urlsplit, urljoin
from concurrent.futures import ThreadPoolExecutor

from requests.models import Response
from requests import Session as _Session
from requests import exceptions as requests_exceptions
from requests.structures import CaseInsensitiveDict as CIDict

from pyxk.utils import (
    make_open,
    LazyLoader,
    get_user_agent,
    download_column,
    string_conversion_digits,
    units_conversion_from_byte,
)

_rich_box = LazyLoader("_rich_box", globals(), "rich.box")
_rich_live = LazyLoader("_rich_live", globals(), "rich.live")
_rich_panel = LazyLoader("_rich_panel", globals(), "rich.panel")
_rich_table = LazyLoader("_rich_table", globals(), "rich.table")
_rich_console = LazyLoader("_rich_console", globals(), "rich.console")



class Session(_Session):

    def __init__(self, *, headers=None, base_url=None, user_agent=None):
        super().__init__()
        headers = CIDict(headers)
        headers.setdefault("User-Agent", user_agent or get_user_agent())
        self.headers.update(headers)
        self._base_url = self.set_base_url(base_url)
        self._console = _rich_console.Console()

    def request(
        self, method, url, *, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None
    ) -> Response:
        # 忽略 requests verify=False 警告
        if not verify:
            import urllib3
            urllib3.disable_warnings()
        url, status, exc_count = self.build_url(url), None, 10
        if show_status:
            status = self._console.status(f"Request <[magenta]{method}[/] [bright_blue u]{url}[/]>", spinner="arc")
            status.start()
        try:
            while True:
                try:
                    response = super().request(
                        method=method, url=url, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json
                    )
                    break
                # Timeout
                except requests_exceptions.Timeout:
                    exc_count -= 1
                    if exc_count < 0:
                        raise
                    warnings.warn(f"Timeout: {timeout!r}", stacklevel=4)
                    time.sleep(1)
                # 连接错误
                except requests_exceptions.ConnectionError as exc:
                    reason = str(exc.args[0])
                    reason_re = ("[Errno 7]", )
                    reason_ok = lambda : True in [item in reason for item in reason_re]
                    if not reason_ok():
                        raise
                    exc_count -= 1
                    if exc_count < 0:
                        raise
                    warnings.warn("Network connection failed", stacklevel=4)
                    time.sleep(1)
        finally:
            if status:
                status.stop()
        return response

    def get(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("GET", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def post(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("POST", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def head(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=False, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("HEAD", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def patch(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("PATCH", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def put(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("PUT", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def options(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("OPTIONS", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def delete(self, url, show_status=True, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None) -> Response:
        return self.request("DELETE", url, show_status=show_status, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

    def build_url(self, url):
        """构造 request url"""
        if not isinstance(url, str):
            return url
        if not self.is_absolute_url(url) and self._base_url:
            return urljoin(self.base_url, url)
        return url

    @staticmethod
    def is_absolute_url(url):
        """判断 绝对url路径"""
        if not url or not isinstance(url, str):
            return False
        url = urlsplit(url)
        if url.scheme and url.netloc:
            return True
        return False

    def set_base_url(self, url):
        """设置 base url"""
        if self.is_absolute_url(url):
            return url
        return None

    @property
    def base_url(self):
        """base url"""
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        self._base_url = self.set_base_url(url)

    def downloader(
        self, url, method="GET", *, output=None, restore=False, transient=False, thread_num=None, show_status=False, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=5, allow_redirects=True, proxies=None, hooks=None, verify=None, cert=None, json=None, stream=True
    ) -> Response:
        """文件下载器

        :params: output: 文件输出路径
        :params: restore: 文件续传
        :params: transient: 文件下载进度 转瞬即逝
        :params: thread_num: 下载线程数量
        :params: show_status: 显示请求状态开关
        """
        req = {
            "headers": headers, "show_status": show_status, "params": params, "data": data, "cookies": cookies, "files": files, "auth": auth, "timeout": timeout, "allow_redirects": allow_redirects, "proxies": proxies, "hooks": hooks, "stream": stream, "verify": verify, "cert": cert, "json": json
        }
        # head
        response = self.head(url, **req)
        req["url"], req["method"] = url, method
        # content length
        length = string_conversion_digits(response.headers.get("Content-Length"))["converted"]
        if not length:
            thread_num, length = 1, None
        # content type
        content_type = response.headers.get("Content-Type")
        # output
        output = os.path.abspath(output) if output and isinstance(output, str) else None
        if not output:
            table = _rich_table.Table(show_header=False, box=_rich_box.SIMPLE_HEAD)
            table.add_column(justify="left", overflow="fold")
            table.add_row(f"<[cyan]Response[/] [{response.status_code}]> [blue u]{url}[/]")
            table.add_section()
            if not length:
                table.add_row("[red]content-length is not available![/]")
                table.add_section()
            table.add_row(f"[green]filetype[/]: [yellow]{content_type}[/]")
            table.add_row(f"[green]filesize[/]: [yellow]{units_conversion_from_byte(length)}[/] ({length})")
            panel = _rich_panel.Panel(
                table, title="[red b]Downloader[red]", title_align="center", border_style="bright_blue"
            )
            self._console.print(panel)
            return response
        # thread_num
        if (
            not output
            or not isinstance(thread_num, int)
            or thread_num <= 0
        ):
            thread_num = 1
        # 线程池
        progress = download_column(add_task=False)
        thread_pool = ThreadPoolExecutor(max_workers=8)

        table = _rich_table.Table(show_header=False, box=_rich_box.SIMPLE_HEAD)
        table.add_column(justify="left", overflow="fold")
        table.add_row(f"<[cyan]Response[/] [{response.status_code}]> [blue u]{url}[/]")
        table.add_section()
        if not length:
            table.add_row("[red]content-length is not available![/]")
            table.add_section()
        table.add_row(f"[green]filetype[/]: [yellow]{content_type}[/]")
        table.add_row(f"[green]filesize[/]: [yellow]{units_conversion_from_byte(length)}[/] ({length})")
        table.add_row(f"[green]filename[/]: [yellow u]{output}[/]")
        table.add_section()
        table.add_row(progress)
        panel = _rich_panel.Panel(
            table,
            title="[red b]Downloader[red]",
            title_align="center",
            border_style="bright_blue",
            subtitle=f"[dim i]thread: {thread_num}[/]",
            subtitle_align="right"
        )
        live, output_list = _rich_live.Live(panel, transient=transient, console=self._console), []
        with live:
            for i in range(thread_num):
                # start_byte, end_byte
                start_byte, end_byte = None, None
                if length:
                    start_byte = i * (length // thread_num)
                    end_byte = start_byte + length // thread_num - 1
                    if i == thread_num - 1:
                        end_byte = length -1
                # output
                download_output = f"{output}.{i}_{thread_num}.temp"
                if thread_num == 1:
                    download_output = output
                output_list.append(download_output)
                # 开启多线程任务
                thread_pool.submit(
                    self._download_chunk,
                    output=download_output,
                    restore=restore,
                    progress=progress,
                    start_byte=start_byte,
                    end_byte=end_byte,
                    **req
                )
            thread_pool.shutdown()
        # 合并多线程下载的视频
        if thread_num > 1:
            self._moviepy_merge(output, output_list)
        return response

    def _download_chunk(
        self, output, progress, restore=False, start_byte=None, end_byte=None, **req
    ):
        total, completed, chunk_size, headers = None, 0, 1024, CIDict(req.pop("headers"))
        # total
        if isinstance(start_byte, int) and isinstance(end_byte, int):
            total = end_byte - start_byte
        else:
            restore = False
        # restore 文件续传
        if restore and os.path.isfile(output):
            completed = os.path.getsize(output)
            if completed  > total + 1:
                restore, completed = False, 0
            else:
                start_byte += completed
        else:
            restore = False
        # 创建 rich.progress -> task
        task = progress.add_task(description="", total=total, completed=completed)
        # headers range
        if isinstance(start_byte, int) and isinstance(end_byte, int):
            headers.update({"Range": f"bytes={start_byte}-{end_byte}"})
        req["headers"] = headers
        # 下载
        response = self.request(**req)
        with make_open(output, "ab" if restore else "wb") as write_fileobj:
            for chunk in response.iter_content(chunk_size=chunk_size):
                write_fileobj.write(chunk)
                progress.update(task, advance=chunk_size)
        response.close()

    @staticmethod
    def _moviepy_merge(output, output_list):
        """合并多线程下载的文件"""
        # 判断文件是否存在
        for file in output_list:
            if not os.path.isfile(file):
                return
        os.rename(output_list.pop(0), output)
        # 创建生成器读取文件
        def read_file(file, chunk_size=1024):
            with open(file, "rb") as read_file:
                while True:
                    chunk = read_file.read(chunk_size)
                    if not chunk:
                        return
                    yield chunk
        # 拼接文件
        with open(output, "ab") as write_file:
            for file in output_list:
                for _chunk in read_file(file):
                    write_file.write(_chunk)
                # 合并完成 删除文件
                os.remove(file)
