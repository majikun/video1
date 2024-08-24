import os
import speech_recognition as sr
from pydub import AudioSegment
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

def extract_audio(video_path, audio_path):
    """从视频中提取音频"""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def recognize_speech_with_timestamps(audio_path):
    """识别音频中的语音并获取每句话的时间戳"""
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_path)
    duration = len(audio) / 1000  # 获取音频总时长（秒）
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        # 获取每句话的时间戳信息
        result = recognizer.recognize_google(audio_data, show_all=True)
        timestamps = []
        if 'alternative' in result:
            for sentence in result['alternative']:
                if 'timestamps' in sentence:
                    for word_info in sentence['timestamps']:
                        word, start_time, end_time = word_info
                        timestamps.append((start_time, end_time))
        return timestamps
    except sr.UnknownValueError:
        print("无法识别音频中的语音")
        return []
    except sr.RequestError as e:
        print(f"请求失败: {e}")
        return []

def split_video_by_speech(video_path, timestamps, output_dir):
    """根据语音识别结果切分视频"""
    os.makedirs(output_dir, exist_ok=True)
    for i, (start_time, end_time) in enumerate(timestamps):
        output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_file)

# 使用示例
video_path = "input_video.mp4"
audio_path = "extracted_audio.wav"
output_dir = "speech_split_videos"

# 提取音频
extract_audio(video_path, audio_path)

# 获取每句话的时间戳
timestamps = recognize_speech_with_timestamps(audio_path)

# 根据时间戳切分视频
if timestamps:
    split_video_by_speech(video_path, timestamps, output_dir)
    print(f"Video split into {len(timestamps)} segments based on speech.")
else:
    print("No speech detected or failed to retrieve timestamps.")
