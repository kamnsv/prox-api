from fastapi import FastAPI
from .api import Routers


app = FastAPI()

routers = Routers()
routers(app)