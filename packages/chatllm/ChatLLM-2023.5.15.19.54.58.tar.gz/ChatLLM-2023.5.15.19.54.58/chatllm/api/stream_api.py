#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : stream_api
# @Time         : 2023/4/28 09:04
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import json

from meutils.pipe import *
from meutils.str_utils import json_loads

from fastapi.responses import Response, StreamingResponse
from fastapi import FastAPI, Form, Depends, File, UploadFile, Body, Request, BackgroundTasks


class ChatApi(FastAPI):

    def __init__(self, title: str = "ChatLLM API", **kwargs):
        super().__init__(title=title, **kwargs)
        self.handler_func = lambda query='自定义 handler_func': query

    def run(self):
        import uvicorn
        uvicorn.run(self)

    def register(self, path='/', handler_func=None, methods=None):
        self.handler_func = handler_func or self.handler_func
        self.api_route(path=path, methods=methods)(self.handler)

    async def handler(self, request: Request):
        input = request.query_params._dict
        body = await request.body()

        if body.startswith(b'{'):  # 主要分支 # json={}
            input.update(json_loads(body))  # json_loads

        query = input.get('query', '')

        if inspect.isgeneratorfunction(self.handler_func):
            return StreamingResponse(self.handler_func(query), media_type='text/event-stream')

        return {'data': self.handler_func(query)}


if __name__ == '__main__':

    app = ChatApi()


    def gen_data(query):
        for i in range(5):
            time.sleep(i)
            yield f"{query} {i}\n"
    def gen_data_(query):
        for i in range(10):
            time.sleep(i)
            yield f"{query} {i}\n"


    app.register('', handler_func=gen_data)
    app.register('/s', handler_func=gen_data_)

    app.run()
