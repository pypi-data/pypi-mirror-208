import asyncio
import json
from typing import Any, List

import aiohttp


class AParser:
    def __init__(self, uri: str, password: str):
        self.password = password
        self.uri = uri
        self._session = aiohttp.ClientSession()

    async def doRequest(self, action: str, data=None, options: dict = {}):
        params = {'password': self.password, 'action': action}

        if data:
            data.update(options)
            params['data'] = data

        body = bytes(json.dumps(params), 'utf-8')
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        async with self._session.post(self.uri, data=body, headers=headers) as response:
            assert response.status in (200, 201), response.status
            data = await response.json()
        return data

    async def ping(self):
        '''
        Checking the server and the API.
        '''
        return await self.doRequest('ping')

    async def info(self):
        '''
        Get general information about A-Parser status and get a list of all available parsers.
        '''
        return await self.doRequest('info')

    async def getProxies(self):
        '''
        Query the list of live proxies. Returns a list of live proxies from all proxies-checkers.
        '''
        return await self.doRequest('getProxies')

    async def getParserPreset(self, parser: str, preset: str):
        '''
        Getting the settings of the specified parser and preset.
        '''
        data = {'parser': parser, 'preset': preset}
        return await self.doRequest('getParserPreset', data)

    async def oneRequest(self, parser: str, preset: str, query: str, **kwargs):
        '''
        A single parsing query, any parser and preset can be used.
        The result will be a generated string in accordance with the format of the result set in the preset, as well as a full log of the parser.
        '''
        data = {'parser': parser, 'preset': preset, 'query': query}
        return await self.doRequest('oneRequest', data, kwargs)

    async def bulkRequest(self, parser: str, preset: str, configPreset: str, threads: int, queries: List[Any], **kwargs):
        '''
        Mass parsing query, any parser and preset can be used, as well as you can specify how many threads to parse.
        The result will be a generated string in accordance with the format of the result set in the preset, as well as a full log of parser work for each thread.
        '''
        data = {'parser': parser, 'preset': preset, 'configPreset': configPreset, 'threads': threads, 'queries': queries}
        return await self.doRequest('bulkRequest', data, kwargs)

    async def addTask(self, parsers: List[Any], configPreset: str, queriesFrom: str, queries: List[str], **kwargs):
        '''
        Adding a task to the queue, all parameters are the same as in the interface of the Task Editor.
        '''
        data = {
            'parsers': parsers, 'configPreset': configPreset, 'queriesFrom': queriesFrom,
            'queries' if queriesFrom == 'text' else 'queriesFile': queries
        }
        return await self.doRequest('addTask', data, kwargs)

    async def getTaskState(self, task_id: int):
        '''
        Getting the job status by its `task_id`.
        '''
        data = {'taskUid': task_id}
        return await self.doRequest('getTaskState', data)

    async def getTaskConf(self, task_id: int):
        '''
        Getting the job configuration by its `task_id`.
        '''
        data = {'taskUid': task_id}
        return await self.doRequest('getTaskConf', data)

    async def changeTaskStatus(self, task_id: int, to_status: str):
        '''
        Change task status by its `task_id`. There are only 4 states into which you can move a task:
        `starting`, `pausing`, `stopping`, `deleting`.
        '''
        data = {'taskUid': task_id, 'toStatus': to_status}
        return await self.doRequest('changeTaskStatus', data)

    async def waitForTask(self, task_id: int, interval: int = 5):
        while True:
            response = await self.getTaskState(task_id)
            if 'data' not in response:
                return response
            state = response['data']
            if state['status'] == 'completed':
                return state
            await asyncio.sleep(interval)

    async def moveTask(self, task_id: int, direction: str):
        '''
        Move a task in the queue by its `task_id`. Possible directions of movement:
        `start`, `end`, `up`, `down`.
        '''
        data = {'taskUid': task_id, 'direction': direction}
        return await self.doRequest('moveTask', data)

    async def getTaskResultsFile(self, task_id: int):
        '''
        Obtaining a link to download the result by job `task_id`.
        From the received link you can download the file only once, without authorization (one-time token is used).
        '''
        data = {'taskUid': task_id}
        return await self.doRequest('getTaskResultsFile', data)

    async def deleteTaskResultsFile(self, task_id: int):
        '''
        Deleting a result file by job `task_id`.
        '''
        data = {'taskUid': task_id}
        return await self.doRequest('deleteTaskResultsFile', data)

    async def getTasksList(self):
        '''
        Getting the list of active tasks.
        If we pass additional parameter completed: 1, we will get the list of completed tasks.
        '''
        return await self.doRequest('getTasksList')

    async def getParserInfo(self, parser: str):
        '''
        Outputs a list of all available results that the specified parser can return.
        '''
        data = {'parser': parser}
        return await self.doRequest('getParserInfo', data)

    async def getAccountsCount(self):
        '''
        Getting the number of active Yandex accounts.
        '''
        return await self.doRequest('getAccountsCount')

    async def update(self):
        '''
        Updates the A-Parser executable file to the latest version available.
        After sending the command, A-Parser will automatically restart.
        The API will return a success response after it has downloaded and updated the executable, this may take 1-3 minutes.
        '''
        return await self.doRequest('update')

    async def close(self) -> None:
        '''
        Closing of the session `aiohttp.ClientSession`
        '''
        if not self._session.closed:
            await self._session.close()


async def main():
    APARSER_URL = '''your A-parser API URL'''
    APARSER_PASS = '''your A-parser API password'''
    task_id = 1
    api = AParser(APARSER_URL, APARSER_PASS)
    print(f'Ping: {await api.ping()}\n')
    print(f'A-parser Info: {await api.info()}\n')
    print(f'File link: {await api.getTaskResultsFile(task_id)}\n')
    print(f'Task state: {await api.getTaskState(task_id)}\n')
    print(f'Task config: {await api.getTaskConf(task_id)}\n')
    print(f'Task list: {await api.getTasksList()}')
    await api.close()


if __name__ == '__main__':
    asyncio.run(main())
