import yt_dlp
import os
import time
import logging
from PIL import Image
import glob

from .previewer import Previewer

class PrevYoutube(Previewer):

    cookiefile = os.getenv('PATH_COOKIE')

    def __str__(self):
        return 'youtube'
    
    def download_ranges(self, duration, n_parts, k_seconds):
        ranges = []
        part_duration = duration / (n_parts + 2)
        for i in range(1, n_parts + 1): # не нужны вступление и титры
            start_time = i * part_duration
            end_time = min(start_time + k_seconds - 4, duration)
            section = {
                'start_time': int(start_time),
                'end_time': int(end_time),
                'title': f'Section_{i}',
                'index': i
            }
            ranges.append(section)
        return ranges


    def download_thumbnail(self, url:str, out_path:str, cover_width:int=None):
        ydl_opts = {
            'skip_download': True,
            'writethumbnail': True,
            'outtmpl': f"{out_path}{os.sep}%(id)s.%(ext)s",
            'cookiefile': self.cookiefile
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url)
            paths = glob.glob(f"{out_path}{os.sep}{result['id']}.*")
            if not len(paths):
                logging.error(f'Download thumbnail for "{url}"')
            
            for thumbnail_path in paths:
                    print('Convert to webp:', thumbnail_path)
                    with Image.open(thumbnail_path) as img:
                        if cover_width:
                            aspect_ratio = img.height / img.width
                            cover_height = int(cover_width * aspect_ratio)
                            img = img.resize((cover_width, cover_height), Image.ANTIALIAS)
                        img.save(f"{out_path}{os.sep}{result['id']}.webp", format='WEBP')


    def download_video(self, url_video: str, out_path: str, n_parts:int, k_seconds:int, timeout=60, retries=5) -> dict: 
        ydl_opts = {
            'format': 'worstvideo[ext=webm]',
            'quiet': True,
            'cookiefile': self.cookiefile,
            'outtmpl': '',
            'socket_timeout': timeout,
            'noprogress': False,
            'retries': retries
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url_video, download=False)
            title = info_dict.get('title', None)         
            formats = info_dict.get('formats', None)  
            orientation = self.determine_video_orientation(formats)
            duration = info_dict.get('duration', None)
            data = {
                'src': url_video,
                'title': title,
                'format': orientation,
                'duration': duration
            }  
            sections = self.download_ranges(duration, n_parts, k_seconds)
            for section in sections:
                print(section)
                index = section['index']
                output_filename = f"{out_path}_{index}_{k_seconds}.webm"
                if os.path.isfile(output_filename):
                    continue
                ydl_opts['outtmpl'] = output_filename
                ydl_opts['download_ranges'] = lambda info_dict, ydl: [section]
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as section_ydl:
                        section_ydl.download([url_video])
                except Exception as e:
                    logging.warning(f'Ошибка загрузки секции #{index} видео "{url_video}" с Youtube: "{e}"')
                    if retries > 0:
                        time.sleep(2)
                        return self.download_video(url_video, out_path, n_parts, k_seconds, timeout, retries - 1)
                    
        return data
        
    def format_time(self, seconds):
        """Форматирует время в строку формата HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def determine_video_orientation(self, formats):
        for f in formats:
            
            if 'width' in f and 'height' in f:
                width = f['width']
                height = f['height']
                
                if height > width:
                    print('format "vertical"', f['width'], f['height'])
                    return "vertical"
                else:
                    print('format "horizontal"', f['width'], f['height'])
                    return "horizontal"
        print('format "unknown"', formats)        
        return "unknown"
    
    @classmethod
    def extract_name(self, url_video: str):
        if 'watch?v=' in url_video:
            return url_video.split('watch?v=')[1]
        return None


if '__main__' == __name__:
    import sys
    # Пример использования
    video_url = sys.argv[1]
    y = PrevYoutube()
    y.create(video_url)