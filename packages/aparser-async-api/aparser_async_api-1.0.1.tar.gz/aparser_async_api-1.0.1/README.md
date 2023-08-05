# aparser-async-api

Asyncio is an alternative [module api-python](https://github.com/a-parser/api-python) for working with A-parser.

- [aparser-async-api](#aparser-async-api)
  - [1. Dependencies](#1-dependencies)
  - [2. Implementation details](#2-implementation-details)
  - [3. Usage example](#3-usage-example)

## 1. Dependencies

- [`aiohttp` 3.8 or never](https://pypi.org/project/aiohttp/);
- [Python 3.7 or newer](https://www.python.org/).

## 2. Implementation details

Adaptation of synchronous code should require a minimum of effort.
All method names are identical to the original ones. The structure of the class is also similar to the original.

## 3. Usage example

```python
import asyncio

from aparser_async_api import AParser

APARSER_URL = '''your A-parser API URL'''
APARSER_PASS = '''your A-parser API password'''


async def main():
    task_id = 1
    api = AParser(APARSER_URL, APARSER_PASS)
    print(f'Ping: {await api.ping()}\n')
    print(f'A-parser Info: {await api.info()}\n')
    print(f'File link: {await api.getTaskResultsFile(task_id)}\n')
    print(f'Task state: {await api.getTaskState(task_id)}\n')
    print(f'Task config: {await api.getTaskConf(task_id)}\n')
    print(f'Task list: {await api.getTasksList()}')
    await api.close()  # Mandatory closure of the session `aiohttp.ClientSession` if you no longer need it


if __name__ == '__main__':
    asyncio.run(main())
```
