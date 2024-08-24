from pydub import AudioSegment

def split_audio(audio_path, segment_length=30):
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) // 1000  # 音频总时长（秒）

    segments = []
    for start_time in range(0, duration, segment_length):
        end_time = min(start_time + segment_length, duration)
        segment = audio[start_time*1000:end_time*1000]
        segment_file = f"segment_{start_time}_{end_time}.wav"
        segment.export(segment_file, format="wav")
        segments.append(segment_file)
    
    return segments

# 使用示例
audio_path = "extracted_audio.wav"
segments = split_audio(audio_path)

print("音频切割为多个片段:", segments)
