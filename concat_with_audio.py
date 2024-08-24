from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip
from gtts import gTTS
import os
import re

def parse_srt_for_subtitles(srt_file):
    """Parses the SRT file and returns a list of tuples (start_time, end_time, text)."""
    with open(srt_file, 'r', encoding="utf-8") as file:
        content = file.read()
    
    pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        start_time = hms_to_seconds(match[0].replace(',', '.'))
        end_time = hms_to_seconds(match[1].replace(',', '.'))
        text = match[2].replace('\n', ' ').strip()
        subtitles.append((start_time, end_time, text))
    
    return subtitles

def hms_to_seconds(hms):
    """Converts a time string HH:MM:SS,ms to seconds."""
    h, m, s = hms.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def generate_audio_for_subtitles(subtitles, lang='en'):
    """Generates audio files for each subtitle using Google TTS."""
    audio_files = []
    durations = []
    for i, (_, _, text) in enumerate(subtitles):
        tts = gTTS(text=text, lang=lang)
        audio_file = f"audio_{i}.mp3"
        tts.save(audio_file)
        audio_clip = AudioFileClip(audio_file)
        audio_files.append(audio_file)
        durations.append(audio_clip.duration)
    return audio_files, durations

def crop_video(video, crop_bottom=50):
    """Crops the video symmetrically on both sides and removes a portion from the bottom."""
    width, height = video.size
    cropped_video = video.crop(x1=0, y1=0, x2=width, y2=height - crop_bottom)
    return cropped_video

def create_final_video_with_tts(video_files, output_file, srt_file, font_path, fps=24, crop_bottom=50):
    clips = []
    subtitles = parse_srt_for_subtitles(srt_file)
    
    # 检查字幕段落数量是否足够
    subtitle_indices = [0, 10, 20, 30]
    if max(subtitle_indices) >= len(subtitles):
        raise ValueError("The subtitle file does not have enough entries to match the selected video clips.")
    
    selected_subtitles = [subtitles[i] for i in subtitle_indices]  # 选择对应的字幕段落

    # Generate TTS audio files and get their durations
    audio_files, durations = generate_audio_for_subtitles(selected_subtitles)
    
    current_time = 0  # 用于记录每个片段在合成视频中的起始时间
    for idx, file in enumerate(video_files):
        try:
            clip = VideoFileClip(file).set_fps(fps)  # 设置帧率
            clip = crop_video(clip, crop_bottom=crop_bottom)  # 裁剪视频
            
            # 获取音频文件和对应的时长
            audio_file = audio_files[idx]
            audio_duration = durations[idx]
            
            # 调整视频片段的时长以匹配音频时长
            clip = clip.set_duration(audio_duration)
            
            # 加载对应的音频文件并设置为视频片段的音频
            audio = AudioFileClip(audio_file).subclip(0, audio_duration)
            clip = clip.set_audio(audio)

            # 获取对应的字幕段落
            _, _, text = selected_subtitles[idx]

            # 创建字幕文本的时间段，指定支持中文的字体
            txt_clip = (TextClip(text, fontsize=28, color='white', font=font_path)
                        .set_position(('center', 'bottom'))
                        .set_start(0)
                        .set_duration(audio_duration))
            
            # 将字幕与视频片段合成
            clip_with_subtitle = CompositeVideoClip([clip, txt_clip]).set_start(current_time)
            clips.append(clip_with_subtitle)

            # 更新当前时间
            current_time += audio_duration
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue
    
    if not clips:
        print("No valid video clips found.")
        return

    # 合并所有视频片段
    final_clip = concatenate_videoclips(clips, method="compose")

    # 导出最终视频
    try:
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', audio_bitrate='128k', bitrate='500k', fps=fps, threads=4)
        print(f"Final video created: {output_file}")
        
    except Exception as e:
        print(f"Error writing final video: {e}")

# 指定视频片段的目录和字幕文件路径
video_directory = 'video_segments'
output_video_file = 'final_cropped_video_with_tts.mp4'
srt_file_path = 'translated_subtitle_full.srt'
font_path = '/System/Library/Fonts/PingFang.ttc'  # macOS 中 PingFang SC 字体的路径

# 获取所有视频文件的列表并按自然顺序排序
all_video_files = sorted([os.path.join(video_directory, file) for file in os.listdir(video_directory) if file.endswith('.mp4')])

# 只选择1, 11, 21, 31 四个片段
selected_video_files = [all_video_files[i] for i in [0, 10, 20, 30]]

# 创建带有字幕的最终视频
create_final_video_with_tts(selected_video_files, output_video_file, srt_file_path, font_path, crop_bottom=60)
