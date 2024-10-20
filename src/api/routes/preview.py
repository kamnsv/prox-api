import os
import uuid
from fastapi import APIRouter, HTTPException, Query

from ..api import API
from ...mods import PrevYoutube

class Previewer(API):



    def set_routes(self, api: APIRouter):

        @api.post('')
        async def create_preview(video_url: str, 
                                 parts: int=Query(5, ge=1, lt=100), 
                                 sec: int=Query(3, ge=1, lt=100),
                                 width:int=Query(640, ge=32, lt=2000), 
                                 height:int=Query(320, ge=32, lt=2000)) -> str:
            
            if 'youtube' in video_url.lower():
                p = PrevYoutube()
                
            try:
                p.create(video_url, n_parts=parts, k_seconds=sec, width=width, height=height)
                return p.target
            except Exception as e:
                raise HTTPException(status_code=400, detail=f'Error create preview: "{e}"')