from youtubesearchpython import VideosSearch
from fastapi import APIRouter
from fastapi import Query
from typing import Union
import os

from ..api import API
from mods.prewyoutube import download_video, split_video, create_preview, extract_youtube_id
class Youtube(API):
    cache_video = 'data/youtube_videocache'
    os.makedirs(cache_video)
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
        
        @api.get('prew')
        async def create_preview(video_url: str, parts: int=5, sec: int=2):
            name = extract_youtube_id(video_url)
            if not os.path.isfile( f'{self.cache_video}/{name}.mp4'):
                download_video(video_url, f'{self.cache_video}/{name}.mp4')
                split_video('video.mp4', parts)  # делим на 5 частей
                create_preview([f'{self.cache_video}/{name}_{i}.webm' for i in range(5)], 2)  # берем по 2 секунды из каждой части
            return 