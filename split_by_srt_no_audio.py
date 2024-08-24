import os
import re
import subprocess

def parse_srt(srt_file):
    """Parses the SRT file and returns a list of tuples (start_time, end_time, text)."""
    with open(srt_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        start_time = match[0].replace(',', '.')
        end_time = match[1].replace(',', '.')
        text = match[2].strip()
        subtitles.append((start_time, end_time, text))
    
    return subtitles

def hms_to_seconds(hms):
    """Converts a time string HH:MM:SS,ms to seconds."""
    h, m, s = hms.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def ffmpeg_extract_subclip_force_reencode(input_file, start_time, end_time, targetname=None):
    """Uses ffmpeg to extract and re-encode a subclip from a video file to avoid black screen."""
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-ss', str(start_time),  # Start time
        '-i', input_file,  # Input file
        '-to', str(end_time - start_time),  # End time
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # Ensure video dimensions are even
        '-c:v', 'libx264',  # Re-encode video with libx264
        '-preset', 'fast',  # Encoding speed/quality trade-off
        '-an',  # Remove audio stream
        targetname
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def cut_video(video_file, srt_file, output_dir):
    """Cuts the video into segments based on the SRT file using ffmpeg with forced re-encoding."""
    subtitles = parse_srt(srt_file)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for i, (start_time, end_time, text) in enumerate(subtitles):
        start_seconds = hms_to_seconds(start_time)
        end_seconds = hms_to_seconds(end_time)
        
        output_file = f"{output_dir}/segment_{i+1:03d}.mp4"
        ffmpeg_extract_subclip_force_reencode(video_file, start_seconds, end_seconds, targetname=output_file)
        print(f"Created {output_file} [{start_time} - {end_time}]")

# Usage
video_file = "preprocessed_video_standard.mp4"  # Replace with your video file path
srt_file = "output_subtitle.srt"  # Replace with your SRT file path
output_dir = "video_segments"  # Replace with your output directory

cut_video(video_file, srt_file, output_dir)
