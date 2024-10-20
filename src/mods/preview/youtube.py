import yt_dlp

from .previewer import Previewer

class PrevYoutube(Previewer):

    def __str__(self):
        return 'youtube'
    
    def download_video(self, url_video: str, out_path: str):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]',
            'outtmpl': out_path,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_video])


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