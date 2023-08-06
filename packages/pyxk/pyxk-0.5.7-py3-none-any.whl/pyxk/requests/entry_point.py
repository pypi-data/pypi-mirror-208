import click
from pyxk.utils import LazyLoader
from pyxk.requests import downloader

_json = LazyLoader("_json", globals(), "json")


def validate_json(ctx, param, value):
    if value is None:
        return None
    try:
        return _json.loads(value)
    except _json.JSONDecodeError:  # pragma: no cover
        raise click.BadParameter("Not valid JSON")

def validate_auth(ctx, param, value):
    if value == (None, None):
        return None
    username, password = value
    if password == "-":  # pragma: no cover
        password = click.prompt("Auth Password", hide_input=True)
    return (username, password)

@click.command()
@click.argument("url", type=str)
@click.option(
    "--method",
    "-m",
    "method",
    type=str,
    help=(
        "Request method, "
        "suah as GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD."
    )
)
@click.option(
    "--params",
    "-p",
    "params",
    type=(str, str),
    multiple=True,
    help="Request parameters.",
)
@click.option(
    "--data",
    "-d",
    "data",
    type=(str, str),
    multiple=True,
    help="Form data.",
)
@click.option(
    "--files",
    "-f",
    "files",
    type=(str, click.File(mode="rb")),
    multiple=True,
    help="Form files.",
)
@click.option(
    "--json",
    "-j",
    "json",
    type=str,
    callback=validate_json,
    help="Json data.",
)
@click.option(
    "--headers",
    "-h",
    "headers",
    type=(str, str),
    multiple=True,
    help="Http headers.",
)
@click.option(
    "--cookies",
    "cookies",
    type=(str, str),
    multiple=True,
    help="Request cookies.",
)
@click.option(
    "--auth",
    "auth",
    type=(str, str),
    default=(None, None),
    callback=validate_auth,
    help="Username and password"
)
@click.option(
    "--proxies",
    "proxies",
    type=str,
    default=None,
    help="Http or https proxies.",
)
@click.option(
    "--timeout",
    "-t",
    "timeout",
    type=float,
    default=5.0,
    help="Http connection timeout(default: 5.0)"
)
@click.option(
    "--no-allow-redirects",
    "allow_redirects",
    is_flag=True,
    default=True,
    help="Disable automatically follow redirects.",
)
@click.option(
    "--no-verify",
    "verify",
    is_flag=True,
    default=True,
    help="Disable SSL verification.",
)
@click.option(
    "--output",
    "-o",
    "output",
    type=str,
    default=None,
    help="Save to file"
)
@click.option(
    "--restore",
    "-r",
    "restore",
    is_flag=True,
    default=False,
    help="Restore connection"
)
@click.option(
    "--thread",
    "thread",
    type=int,
    default=1,
    help="Multithreaded download"
)
def main(
    method, url, params, headers, data, json, files, cookies, auth, proxies, timeout, allow_redirects, verify, output, restore, thread,
):
    if not method:
        method = "POST" if data or files or json else "GET"
    downloader(
        method=method,
        url=url,
        params=dict(params) or None,
        headers=dict(headers) or None,
        json=json or None,
        files=dict(files) or None,
        cookies=dict(cookies) or None,
        proxies=proxies,
        timeout=timeout,
        allow_redirects=allow_redirects,
        verify=verify,
        auth=auth,
        output=output,
        restore=restore,
        thread_num=thread,
    )
