# Asycio Gpsd Client

# Install

```shell
pip install asyncio-gpsd-client
```

# Usage

```python
import asyncio

from asyncio_gpsd_client import GpsdClient

HOST = "127.0.0.1"
PORT = 2947


async def main():
    async with GpsdClient(HOST, PORT) as client:
        print(await client.poll())  # Get gpsd POLL response
        while True:
            print(await client.get_result())  # Get gpsd TPV responses


asyncio.run(main())
```
