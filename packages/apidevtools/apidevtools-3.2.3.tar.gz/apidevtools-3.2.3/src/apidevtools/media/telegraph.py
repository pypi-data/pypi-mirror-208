import contextlib as _contextlib
import aiohttp as _aiohttp
import io


async def upload(file: io.BytesIO, mime: str = 'image/png') -> str | None:
    """
    Upload media to telegra.ph
    :param file:
    :param mime:
    :return:
    """
    data = _aiohttp.FormData(dict(name='file', value=file.read(), content_type=mime, filename=f"file.{mime.split('/')[1]}"))
    with _contextlib.suppress(_aiohttp.ClientError):
        async with _aiohttp.ClientSession(connector=_aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(url='https://telegra.ph/upload', data=data) as response:
                sources = await response.json()
                if not (isinstance(sources, dict) and sources.get('error')):
                    return f"https://telegra.ph{sources[-1]['src']}"


async def download(url: str) -> bytes | None:
    """
    Download media from any source
    :param url:
    :return:
    """
    async with _aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()
