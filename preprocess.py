import subprocess

def preprocess_video_with_keyframes_and_fps(input_file, output_file, target_fps=30, target_bitrate="2M", gop_size=30):
    """Preprocess the video by re-encoding it with a forced keyframe interval (GOP size) and standard frame rate."""
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', input_file,  # Input file
        '-r', str(target_fps),  # Set target frame rate
        '-b:v', target_bitrate,  # Set target video bitrate
        '-g', str(gop_size),  # Set GOP (Group of Pictures) size, force keyframe every gop_size frames
        '-keyint_min', str(gop_size),  # Minimum interval between keyframes
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # Ensure video dimensions are even
        '-c:v', 'libx264',  # Encode video using H.264
        '-preset', 'fast',  # Encoding speed/quality trade-off
        '-c:a', 'aac',  # Re-encode audio using standard AAC-LC
        '-b:a', '192k',  # Set audio bitrate
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print(f"Preprocessed video saved to {output_file}")

# Usage
input_video_file = "input_video.mp4"  # Replace with your input video file path
preprocessed_video_file = "preprocessed_video_standard.mp4"  # Replace with your desired output file path

preprocess_video_with_keyframes_and_fps(input_video_file, preprocessed_video_file)
