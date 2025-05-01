import yt_dlp
import sys
import subprocess
import os
import argparse # Import argparse

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

def main(video_url, start_time=None, end_time=None):
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()

    # Base settings for downloading and converting to mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        # Add start/end times to the filename if provided
        'outtmpl': f'%(title)s_%(id)s_start{start_time}_end{end_time}.%(ext)s' if start_time is not None and end_time is not None else '%(title)s_%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256', # High quality base
            # REMOVE postprocessor_args from here
        }],
        'noplaylist': True,
        'verbose': True
    }

    # Add ffmpeg location if found
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
        print(f"Using FFmpeg from: {ffmpeg_path}")
        ffprobe_path = os.path.join(ffmpeg_path, 'ffprobe')
        if os.path.exists(ffprobe_path):
            print(f"Found ffprobe at: {ffprobe_path}")
        else:
            print(f"Warning: ffprobe not found at {ffprobe_path}")
    else:
        print("Warning: FFmpeg path not found. Make sure FFmpeg is installed.")
        print("Try installing FFmpeg with: brew install ffmpeg")
        return

    # Add TOP-LEVEL postprocessor args for time segment if start and end times are provided
    if start_time is not None and end_time is not None:
        # Add the arguments to the main ydl_opts dictionary
        ydl_opts['postprocessor_args'] = [
            '-ss', str(start_time), # Start time
            '-to', str(end_time)    # End time
        ]
        print(f"Configured to download segment from {start_time}s to {end_time}s.")
    elif start_time is not None or end_time is not None:
        print("Warning: Both start and end times must be provided to download a segment. Downloading full audio.")


    # Download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            download_segment_info = f" (segment: {start_time}s-{end_time}s)" if start_time is not None and end_time is not None else ""
            print(f"🎧 Downloading audio from: {video_url}{download_segment_info}")
            info = ydl.extract_info(video_url, download=True)

            # Determine the filename after download and postprocessing
            final_filepath = None
            # Try getting path from 'requested_downloads' first (often more reliable after PP)
            if 'requested_downloads' in info and info['requested_downloads']:
                 final_filepath = info['requested_downloads'][0].get('filepath')
            # Fallback to top-level 'filepath' if available
            elif 'filepath' in info:
                 final_filepath = info.get('filepath')

            # If we still couldn't determine the path, construct it based on outtmpl
            if not final_filepath:
                 print("Warning: Could not automatically determine final file path from yt-dlp info. Constructing from template.")
                 # Construct filename based on the template and info
                 if 'entries' in info: # Playlist (using first entry)
                     downloaded_file_info = info['entries'][0]
                 else: # Single video
                     downloaded_file_info = info

                 # Use ydl.prepare_filename to handle template substitution more robustly
                 try:
                     # Ensure the extension matches the postprocessor output
                     temp_info_for_filename = downloaded_file_info.copy()
                     temp_info_for_filename['ext'] = ydl_opts['postprocessors'][0]['preferredcodec']
                     # Add start/end time info if segmenting
                     if start_time is not None and end_time is not None:
                         temp_info_for_filename['title'] = f"{temp_info_for_filename.get('title', 'unknown_title')}_start{start_time}_end{end_time}"

                     final_filepath = ydl.prepare_filename(temp_info_for_filename)
                     # prepare_filename might give the original extension, force mp3
                     base, _ = os.path.splitext(final_filepath)
                     final_filepath = base + '.' + ydl_opts['postprocessors'][0]['preferredcodec']

                 except Exception as e:
                     print(f"Error constructing filename from template: {e}")
                     # Fallback to a simpler manual construction if prepare_filename fails
                     base_filename_template = ydl_opts['outtmpl'].replace('.%(ext)s', '')
                     base_filename = base_filename_template.replace('%(title)s', downloaded_file_info.get('title', 'unknown_title'))
                     base_filename = base_filename.replace('%(id)s', downloaded_file_info.get('id', 'unknown_id'))
                     # Add start/end if applicable (already part of template now)
                     # base_filename = base_filename.replace('_start{start_time}_end{end_time}', f'_start{start_time}_end{end_time}' if start_time is not None else '')
                     final_filepath = base_filename + '.' + ydl_opts['postprocessors'][0]['preferredcodec']


            if final_filepath and os.path.exists(final_filepath):
                print(f"✅ High-quality MP3 ({ydl_opts['postprocessors'][0]['preferredquality']}k){download_segment_info} ready: {final_filepath}")
                # Create low quality version
                convert_to_low_quality(final_filepath, ffmpeg_path)
            elif final_filepath:
                 print(f"Error: Expected file not found after download/processing: {final_filepath}")
                 # Attempt to list files in the directory to help debug
                 try:
                     print("Files in current directory:")
                     for item in os.listdir('.'):
                         print(f"- {item}")
                 except OSError as list_err:
                     print(f"Could not list directory contents: {list_err}")
            else:
                 print("Error: Could not determine the downloaded file path.")


    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading or processing: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure FFmpeg is properly installed and accessible")
        print("2. Check if the video URL is correct and accessible")
        print("3. Ensure you have write permissions in the current directory")
        if start_time is not None:
             print("4. Segment downloading relies heavily on FFmpeg. Ensure it's working correctly and the times are valid for the video.")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Download YouTube audio and optionally convert a segment.")
    parser.add_argument("url", nargs='?', help="URL of the YouTube video. If omitted, uses a default.", default=None)
    parser.add_argument("-s", "--start", type=int, help="Start time for the segment in seconds.", default=None)
    parser.add_argument("-e", "--end", type=int, help="End time for the segment in seconds.", default=None)

    args = parser.parse_args()

    # Determine video URL
    video_url = args.url
    if not video_url:
        # Use default URL if none provided
        video_id = "882ba_OmWXE" # Example video ID
        video_url = f"https://youtu.be/{video_id}"
        print(f"URL not specified, using default: {video_url}")

    # Validate start/end times
    if (args.start is not None and args.end is None) or (args.start is None and args.end is not None):
        print("Error: Both --start and --end must be provided together to extract a segment.")
        sys.exit(1) # Exit if only one is provided
    if args.start is not None and args.end is not None and args.start >= args.end:
         print(f"Error: Start time ({args.start}) must be less than end time ({args.end}).")
         sys.exit(1)


    # Call main function with parsed arguments
    main(video_url, args.start, args.end)
