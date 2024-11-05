from abc import ABC, abstractmethod
import os
import logging
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
from moviepy.video.fx.all import speedx
from PIL import Image
Image.ANTIALIAS = Image.Resampling.LANCZOS

from ..scavenger import remove_old

class Previewer(ABC):
    path_data = os.getenv('PATH_DATA', 'data')
    cache_preview = f'{path_data}{os.sep}prev'
    download_path = f'{path_data}{os.sep}src'
    path_metadata = f'{path_data}{os.sep}meta'
    path_covers = f'{path_data}{os.sep}cover'
    max_save = {"prev": 1000, "download": 100}

    @abstractmethod
    def __str__(self):
        ...

    def create(self, video_url: str, n_parts=5, k_seconds=3, width=None, height=None, speed=1, cover_width=640):
        print(video_url)
        os.makedirs(self.cache_preview + os.sep + str(self), exist_ok=True)
        os.makedirs(self.download_path + os.sep + str(self), exist_ok=True)
        os.makedirs(self.path_metadata + os.sep + str(self), exist_ok=True)
        os.makedirs(self.path_covers + os.sep + str(self), exist_ok=True)
        self.name = self.extract_name(video_url)
        size = '' if width is None else f'{width}x{height}'
        self.target = os.path.join(self.cache_preview, str(self), f'{self.name}_{size}_{n_parts:02}_{k_seconds:02}_{speed}.webm')
        self.src = os.path.join(self.download_path, str(self), f'{self.name}')
        self.meta = os.path.join(self.path_metadata, str(self), f'{self.name}.json')
        self.cover = os.path.join(self.path_covers, str(self), f'{self.name}.webp')
        if not os.path.isfile(self.cover):
            self.download_thumbnail(video_url, os.path.join(self.path_covers, str(self)), cover_width)
        
        data = video_url
        if os.path.isfile(self.meta):
            with open(self.meta, 'r') as f:
                data = json.load(f)
            data['preview'] = self.target
            data['thumbnail'] = self.cover

        if not os.path.isfile(self.target):
            #remove_old(self.cache_preview, self.max_save['prev'])
            #remove_old(self.download_path, self.max_save['download'])
            #remove_old(self.path_metadata, self.max_save['download'])
            if not os.path.isfile(self.meta):
                try:
                    data = self.download_video(video_url, self.src, n_parts, k_seconds)
                except Exception as e: 
                    logging.error(e)
                    data = self.download_video(video_url, self.src, n_parts, k_seconds)
                with open(self.meta, 'w') as f:
                    json.dump(data, f)
                data['preview'] = self.target
                data['thumbnail'] = self.cover
            if 'vertical' == data['format']:
                 width, height = height, width
            self.create_preview(self.src + f'_%s_{k_seconds}.webm', self.target, n_parts, width, height, speed)



        return data
    
    @abstractmethod
    def download_thumbnail(self, url:str, out_path:str, cover_width:int):
        ...

    @abstractmethod
    def extract_name(self, url_video: str):
        ...

    @abstractmethod
    def download_video(self, url_video: str, out_path: str, n_parts:int, k_seconds:int):
        ...
    
    def create_preview(self, template_path:str, output:str, n_parts: int, width:int=None, height:int=None, speed=1.1, audio=False):
        preview = []
        #transition = ColorClip(size=(width, height), color=(0, 0, 0), duration=1)
        for i in range(1, n_parts + 1):
            fname = template_path % i
            if not os.path.isfile(fname):
                logging.warning(f'Часть #{i} файла "{fname}" для склейки превью не найдена')
                continue
            try:
                clip = VideoFileClip(fname, audio=audio)  
                if width is not None:
                    clip = clip.resize(newsize=(width, height))
                if speed != 1:
                    clip = speedx(clip, factor=speed)
                # = clip.fadein(0.3).fadeout(0.7)
                preview.append(clip)
                #preview.append(transition)
                clip.close()
            except Exception as e:
                 logging.warning(f'Часть #{i} файла "{fname}" для склейки не загрузилась: "{e}"')
                 #self.remove_badvideo(fname)

        try:
            final_clip = concatenate_videoclips(preview, method="compose")
            final_clip.write_videofile(output, codec="libvpx", audio=audio)
        except Exception as e:
            logging.warning(f'Склеить превью "{fname}" не удалось: "{e}"')
        finally:
            final_clip.close()

    def split_and_preview(self, video_path:str, output_path:str, n_parts: int, k_seconds: int, width:int=640, height:int=320, speed_factor=1.1, audio=False):
        clip = VideoFileClip(video_path, audio=False)
        duration = clip.duration
        part_duration = duration / (n_parts + 2)

        preview_clips = []
        for i in range(1, n_parts-1):
            start = i * part_duration
            end = min(start + k_seconds * speed_factor, (i + 1) * part_duration)

            part_clip = clip.subclip(start, end)
            part_clip = part_clip.resize(newsize=(width, height))
            part_clip = speedx(part_clip, factor=speed_factor)
            preview_clips.append(part_clip)

            transition = ColorClip(size=(width, height), color=(0, 0, 0), duration=1)
            preview_clips.append(transition)

        final_clip = concatenate_videoclips(preview_clips, method="compose")

        final_clip.write_videofile(output_path, codec="libvpx", audio=False)

        clip.close()
        final_clip.close()
