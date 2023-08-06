
App guardians.

# Usage
```python
import asyncio
from typing import Any, Dict

from codefast.asyncio.rabbitmq import consume
from rich import print

from custodes.server import get
from custodes.client import post

async def main():
    return await asyncio.gather(
        post('custodes server', {'code': 0, 'message': 'OK'}, loop=True, expire=120),
        get()
    )

if __name__ == '__main__':
    cf.info('custodes server started...')
    asyncio.run(main())

```
