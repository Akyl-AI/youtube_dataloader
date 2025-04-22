import yt_dlp
import sys
import subprocess
import os

def get_ffmpeg_path():
    """Determine the path to ffmpeg executable"""
    try:
        # Try to find ffmpeg using 'which' command
        result = subprocess.run(['which', 'ffmpeg'], 
                               capture_output=True, 
                               text=True, 
                               check=False)
        if result.returncode == 0:
            ffmpeg_path = os.path.dirname(result.stdout.strip())
            
            # Verify that ffprobe is also available in the same directory
            ffprobe_path = os.path.join(ffmpeg_path, 'ffprobe')
            if os.path.exists(ffprobe_path):
                return ffmpeg_path
        
        # Check common locations
        common_paths = [
            '/opt/homebrew/bin',
            '/usr/local/bin',
            '/usr/bin'
        ]
        
        for path in common_paths:
            ffmpeg_file = os.path.join(path, 'ffmpeg')
            ffprobe_file = os.path.join(path, 'ffprobe')
            if os.path.exists(ffmpeg_file) and os.path.exists(ffprobe_file):
                return path
                
        return None
    except Exception as e:
        print(f"Error finding FFmpeg: {e}")
        return None

def main(video_url):
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()
    
    # Настройки для скачивания и конвертации в mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'noplaylist': True,
        'verbose': True  # Add verbose output for debugging
    }
    
    # Add ffmpeg location if found
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
        print(f"Using FFmpeg from: {ffmpeg_path}")
        
        # Verify ffprobe exists
        ffprobe_path = os.path.join(ffmpeg_path, 'ffprobe')
        if os.path.exists(ffprobe_path):
            print(f"Found ffprobe at: {ffprobe_path}")
        else:
            print(f"Warning: ffprobe not found at {ffprobe_path}")
    else:
        print("Warning: FFmpeg path not found. Make sure FFmpeg is installed.")
        print("Try installing FFmpeg with: brew install ffmpeg")
        return

    # Скачивание
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"🎧 Скачиваю аудио с: {video_url}")
            ydl.download([video_url])
            print("✅ Готово!")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure FFmpeg is properly installed")
        print("2. Try reinstalling FFmpeg: brew reinstall ffmpeg")
        print("3. Check if the video is available in your region")

if __name__ == "__main__":
    # Если скрипт запущен напрямую, проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Используем URL из аргументов командной строки
        video_url = sys.argv[1]
    else:
        # Используем URL по умолчанию
        video_id = "882ba_OmWXE"
        video_url = f"https://youtu.be/{video_id}"
        print(f"URL не указан, используется URL по умолчанию: {video_url}")
    
    main(video_url)
