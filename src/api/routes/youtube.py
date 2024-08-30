from youtubesearchpython import VideosSearch
from fastapi import APIRouter
from fastapi import Query
from typing import Union

from ..api import API

class Youtube(API):

    cache = {}

    def set_routes(self, api: APIRouter):
        @api.post('')
        async def search(query: str, max_links: int = Query(10, ge=1, lt=100), name = None) -> Union[list, dict]:
            
            if (query, max_links) in self.cache:
                video_links = self.cache.get((query, max_links))
            else:
                videos_search = VideosSearch(query, limit=max_links)
                results = videos_search.result()['result']
                
                video_links = []
                for video in results:
                    video_links.append(video['link'])

                self.cache[(query, max_links)] = video_links
            
            if name:
                return {name: video_links}
            return video_links