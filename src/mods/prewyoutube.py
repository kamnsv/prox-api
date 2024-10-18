import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
import yt_dlp
from PIL import Image

# Устанавливаем корректный фильтр для Pillow (LANCZOS вместо ANTIALIAS)
Image.ANTIALIAS = Image.Resampling.LANCZOS


def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': output_path,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def split_and_preview(video_path: str, n_parts: int, k_seconds: int, output_path: str, width=640, height=320):
    """Разбивает видео на n частей, выбирает по k секунд из каждой и объединяет с переходами."""
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

        # Добавляем переход с черным экраном (1 секунда)
        transition = ColorClip(size=(width, height), color=(0, 0, 0), duration=1)
        preview_clips.append(transition)

    final_clip = concatenate_videoclips(preview_clips[:-1], method="compose")

    final_clip.write_videofile(output_path, codec="libvpx", audio=False)

    clip.close()
    final_clip.close()
    
def extract_youtube_id(url):
    # Разделяем URL по символу '=' и берем последний элемент
    if 'watch?v=' in url:
        return url.split('watch?v=')[1]
    return None


if '__main__' == __name__:
    import sys
    # Пример использования
    video_url = sys.argv[1]
    id_name = extract_youtube_id(video_url)
    download_video(video_url, f'{id_name}.mp4')
    split_and_preview(f'{id_name}.mp4', n_parts=5, k_seconds=3, output_path=f'{id_name}.webm')
    