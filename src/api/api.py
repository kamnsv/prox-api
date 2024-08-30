from abc import ABC, abstractmethod
from fastapi import APIRouter


class API(ABC):
    def __call__(self) -> APIRouter:
        api = APIRouter()
        self.set_routes(api)
        return api
    
    @abstractmethod
    def set_routes(self, api: APIRouter):
        ...

