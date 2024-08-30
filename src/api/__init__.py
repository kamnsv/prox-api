from fastapi import FastAPI

from .routes import Youtube

class Routers:

    def __call__(self, app: FastAPI):
        app.include_router(Youtube()(), prefix='/api/youtube')
            
       