from fastapi import FastAPI

from .routes import Youtube, OpenAI, Previewer

class Routers:

    def __call__(self, app: FastAPI):
        app.include_router(Youtube()(), prefix='/api/youtube')
        app.include_router(OpenAI()(), prefix='/api/chatgpt')
        app.include_router(Previewer()(), prefix='/api/preview')    
       