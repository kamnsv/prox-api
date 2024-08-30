import uvicorn
from src.cfg import server_host, server_port
from src import app

uvicorn.run(app=app, 
            host=server_host, 
            port=server_port)
