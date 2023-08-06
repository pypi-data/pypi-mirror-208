import os
from typing import Callable

from elefantolib import context
from elefantolib.provider import fastapi_provider

import fastapi
from fastapi import routing

from redis import asyncio as aioredis

from .requests import Request


class APIRoute(routing.APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: fastapi.Request) -> fastapi.Response:
            pvr = fastapi_provider.FastAPIProvider(request=request)
            request.scope['pfm'] = context.AsyncPlatformContext(pvr=pvr)

            if redis_url := os.environ.get('REDIS_URL'):
                request.scope['redis'] = aioredis.from_url(redis_url)

            new_request = Request(request.scope, request.receive)
            return await original_route_handler(new_request)
        return custom_route_handler
