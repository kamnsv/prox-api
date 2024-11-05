from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pathlib import Path
import logging

from ..api import API
from ...mods import PrevYoutube

class Previewer(API):

    def set_routes(self, api: APIRouter):
        @api.post('_list')
        async def handle_list(
                                list_urls: dict, 
                                parts: int=Query(5, ge=1, lt=100), 
                                sec: int=Query(5, ge=5, lt=100),
                                speed: float = 1.1,
                                width:int|None = None, 
                                height:int|None = None,
                                cover_width:int|None = None,
                                ) -> dict:
            p = PrevYoutube()
            if not width : width = None
            if not height : height = None
            if not cover_width : cover_width = None
            try:
                return {name: [p.create(video_url, n_parts=parts, k_seconds=sec, width=width, height=height, speed=speed, cover_width=cover_width) 
                               for video_url in urls]
                                    for name, urls in list_urls.items()}
            except Exception as e:
                s = f'Error handle list create preview: "{e}"'
                logging.error(s)
                raise HTTPException(status_code=500, detail=s)

        @api.post('')
        async def create_preview(video_url: str, 
                                 parts: int=Query(5, ge=1, lt=100), 
                                 sec: int=Query(5, ge=5, lt=100),
                                 speed: float = 1.1,
                                 width:int|None = None, 
                                 height:int|None = None, 
                                 cover_width:int|None = None,
                                ) -> dict:
            if not width : width = None
            if not height : height = None
            if not cover_width : cover_width = None
            p = None
            if 'youtube' in video_url.lower():
                p = PrevYoutube()

            if p is None:
                raise HTTPException(status_code=404, detail=f'Not found previewer for "{video_url}"')

            try:
                data = p.create(video_url, n_parts=parts, k_seconds=sec, width=width, height=height, speed=speed, cover_width=cover_width)
                video_path = Path(p.target)
                if not video_path.is_file():
                    raise HTTPException(status_code=404, detail='Video create, but not found "{p.target}"')

                return data#StreamingResponse(open(video_path, "rb"), media_type="video/webm")
            except Exception as e:
                s = f'Error create preview: "{e}"'
                logging.error(s)
                raise HTTPException(status_code=500, detail=s)
                      