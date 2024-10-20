from abc import ABC, abstractmethod
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
from PIL import Image
Image.ANTIALIAS = Image.Resampling.LANCZOS

from ..scavenger import remove_old

class Previewer(ABC):

    cache_preview = '/data/video_preview'
    download_path = '/data/video_src'
    max_save = {"prev": 1000, "download": 100}

    @abstractmethod
    def __str__(self):
        ...

    def create(self, video_url: str, cookies: str, n_parts=5, k_seconds=3, width=640, height=320):

        os.makedirs(self.cache_preview + os.sep + str(self), exist_ok=True)
        os.makedirs(self.download_path + os.sep + str(self), exist_ok=True)

        self.name = self.extract_name(video_url)
        self.target = os.path.join(self.cache_preview, str(self), f'{self.name}__{width}x{height}_{n_parts:02}_{k_seconds:02}.webm')
        self.src = os.path.join(self.download_path, str(self), f'{self.name}.mp4')
             
        if not os.path.isfile(self.target):
            
            if not os.path.isfile(self.target): 
                remove_old(self.cache_preview, self.max_save['prev'])
                remove_old(self.download_path, self.max_save['download'])
                self.download_video(video_url, self.src, cookies)
        
            self.split_and_preview(self.src, n_parts, k_seconds, self.target, width, height)
    
    @abstractmethod
    def extract_name(self, url_video: str):
        ...

    @abstractmethod
    def download_video(self, url_video: str, out_path: str, cookies: str=''):
        ...
    
    def split_and_preview(self, video_path, output_path:int, n_parts: int, k_seconds: int, width:int=640, height:int=320, audio=False):
        clip = VideoFileClip(video_path, audio=False)
        duration = clip.duration
        part_duration = duration / n_parts

        preview_clips = []
        for i in range(n_parts):
            start = i * part_duration
            end = min(start + k_seconds, (i + 1) * part_duration)

            part_clip = clip.subclip(start, end)
            part_clip = part_clip.resize(newsize=(width, height))
            preview_clips.append(part_clip)

            transition = ColorClip(size=(width, height), color=(0, 0, 0), duration=1)
            preview_clips.append(transition)

        final_clip = concatenate_videoclips(preview_clips[:-1], method="compose")

        final_clip.write_videofile(output_path, codec="libvpx", audio=False)

        clip.close()
        final_clip.close()
