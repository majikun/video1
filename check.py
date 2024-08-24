import traceback
from moviepy.editor import VideoFileClip
import numpy as np
import os

def check_audio_format(file):
    try:
        print(f"Processing file: {file}")
        clip = VideoFileClip(file)
        if clip.audio is None:
            print(f"No audio found in {file}")
        else:
            print(f"Audio duration: {clip.audio.duration} seconds")
            print(f"Audio fps: {clip.audio.fps}")
            chunksize = 44100 * 2 * clip.audio.nchannels  # Example calculation
            chunks = []
            for i, chunk in enumerate(clip.audio.iter_chunks(fps=44100, quantize=True, nbytes=2, chunksize=chunksize)):
                try:
                    print(f"Processing chunk {i} with shape: {chunk.shape}")
                    if chunk is not None and len(chunk) > 0:  # Filter out empty chunks
                        chunks.append(chunk)
                    else:
                        print(f"Empty or invalid chunk found in {file}, chunk {i}")
                except IndexError as e:
                    print(f"IndexError processing chunk {i} in {file}: {e}")
                    traceback.print_exc()
                    break  # Stop processing further chunks if an error occurs

            if chunks:
                audio_array = np.vstack(chunks)
                print(f"Audio array type: {type(audio_array)}")
                print(f"Audio array shape: {audio_array.shape}")
            else:
                print(f"No valid audio chunks to process in {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")

# 指定视频片段的目录和字幕文件路径
video_directory = 'video_segments'
output_video_file = 'final_video_with_subtitles.mp4'
srt_file_path = 'output_subtitle.srt'

# 获取所有视频文件的列表并按自然顺序排序
all_video_files = sorted([os.path.join(video_directory, file) for file in os.listdir(video_directory) if file.endswith('.mp4')])

# 筛选出奇数文件
odd_video_files = [file for i, file in enumerate(all_video_files) if i % 2 == 0]

for file in all_video_files:
    check_audio_format(file)
