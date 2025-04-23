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

def convert_to_low_quality(input_file, ffmpeg_path=None):
    """Convert high quality MP3 to low quality version"""
    # Create low quality filename by adding '_low' before the extension
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_low{ext}"
    
    # FFmpeg command to convert to low quality (64k bitrate)
    ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-b:a', '64k', output_file]
    
    # Use specified ffmpeg path if provided
    if ffmpeg_path:
        ffmpeg_cmd[0] = os.path.join(ffmpeg_path, 'ffmpeg')
    
    try:
        print(f"🔄 Converting to low quality: {output_file}")
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"✅ Low quality version created: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error converting to low quality: {e}")
        print(f"FFmpeg error output: {e.stderr.decode() if e.stderr else 'None'}")
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
            info = ydl.extract_info(video_url, download=True)
            
            # Get the filename of the downloaded file
            if 'entries' in info:
                # Playlist
                downloaded_file = ydl.prepare_filename(info['entries'][0])
            else:
                # Single video
                downloaded_file = ydl.prepare_filename(info)
            
            # Change extension to mp3 since it's been converted
            downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3'
            
            print(f"✅ Высококачественный MP3 (256k) готов: {downloaded_file}")
            
            # Create low quality version
            if os.path.exists(downloaded_file):
                convert_to_low_quality(downloaded_file, ffmpeg_path)
            else:
                print(f"Error: Could not find downloaded file: {downloaded_file}")
    
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
