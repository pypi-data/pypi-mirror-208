from fastapi import requests


class Request(requests.Request):

    @property
    def pfm(self):
        pfm = self.scope['pfm']
        pfm.validate()
        return pfm

    @property
    def redis(self):
        return self.scope.get('redis')
