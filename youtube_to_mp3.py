#!/usr/bin/env python3
"""
YouTube to MP3 Converter using yt-dlp

This script downloads YouTube videos and converts them to MP3 format.
"""

import sys
import os
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)


def download_youtube_to_mp3(url, output_path="downloads", custom_filename=None):
    """
    Download a YouTube video and convert it to MP3.
    
    Args:
        url (str): YouTube video URL
        output_path (str): Directory to save the MP3 file
        custom_filename (str): Optional custom filename (without extension)
    """
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Determine output template
    if custom_filename:
        # Remove .mp3 extension if user added it
        if custom_filename.endswith('.mp3'):
            custom_filename = custom_filename[:-4]
        output_template = os.path.join(output_path, f'{custom_filename}.%(ext)s')
    else:
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [progress_hook],
    }
    
    try:
        print(f"\nDownloading from: {url}")
        print(f"Output directory: {os.path.abspath(output_path)}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info to get video title
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            print(f"Video: {video_title}")
            
            if custom_filename:
                print(f"Filename: {custom_filename}.mp3\n")
            else:
                print(f"Filename: {video_title}.mp3\n")
            
            # Download and convert
            ydl.download([url])
            
        print(f"\n✓ Successfully downloaded and converted to MP3!")
        print(f"✓ Saved to: {os.path.abspath(output_path)}")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        sys.exit(1)


def progress_hook(d):
    """Hook to display download progress."""
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\rDownloading: {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
        except:
            pass
    elif d['status'] == 'finished':
        print("\nDownload complete! Converting to MP3...")


def main():
    """Main function to handle command-line usage."""
    print("=" * 60)
    print("YouTube to MP3 Converter")
    print("=" * 60)
    
    # Get URL from command line or prompt user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nEnter YouTube URL: ").strip()
    
    if not url:
        print("Error: No URL provided.")
        sys.exit(1)
    
    # Get output directory
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = input("Enter output directory (press Enter for 'downloads'): ").strip()
        if not output_path:
            output_path = "downloads"
    
    # Get custom filename
    if len(sys.argv) > 3:
        custom_filename = sys.argv[3]
    else:
        custom_filename = input("Enter custom filename (press Enter to use video title): ").strip()
        if not custom_filename:
            custom_filename = None
    
    # Download and convert
    download_youtube_to_mp3(url, output_path, custom_filename)


if __name__ == "__main__":
    main()

