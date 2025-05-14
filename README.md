# YouTube Audio Downloader

A simple Python script that downloads audio from YouTube videos and converts them to MP3 format.

## Description

This tool uses the `yt-dlp` library to download audio from YouTube videos and automatically convert them to MP3 format with 256kbps quality. It's designed to be simple to use, requiring just a YouTube URL to function.

## Requirements

- Python 3
- yt-dlp library
- FFmpeg (located at `/opt/homebrew/bin` for Mac M1/M2)

## Installation

1. Make sure you have Python 3 installed
2. Install the required library:
```
pip install yt-dlp
```
3. Install FFmpeg (if not already installed):

## Usage

### Basic Usage

Run the script with a YouTube URL as an argument:
```
python main.py https://youtu.be/YOUR_VIDEO_ID
```

### Downloading Audio Segments
You can download a specific segment of the audio by providing start and end times in seconds using the --start and --end flags. Both flags must be used together.

Example: Download audio from 30 seconds to 120 seconds:
```
python main.py https://youtu.be/YOUR_VIDEO_ID --start 30 --end 120
```

### Downgrade an Existing MP3 to Low Quality
You can convert any existing MP3 file to a low quality (64kbps) version using the `--downgrade` flag:
```
python main.py --downgrade your_audio.mp3
```
This will create a new file with `_low` added to the filename, e.g., `your_audio_low.mp3`.

### Default URL

If no URL is provided, the script will use a default YouTube video:
```
python main.py
```


This will download audio from the default video (ID: 882ba_OmWXE).

## How It Works

1. The script takes a YouTube URL as input
2. It configures yt-dlp to extract the best available audio
3. FFmpeg processes the audio and converts it to MP3 format
4. The resulting MP3 file is saved with the video's title as the filename

## Customization

You can modify the script to change:
- Audio quality (currently set to 256kbps)
- Output filename format
- Audio format (currently MP3)


