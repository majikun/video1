from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech

def convert_to_mono(audio_file_path, output_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(output_file_path, format="wav")
    return output_file_path

def get_sample_rate(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    return audio.frame_rate

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient()

    # 自动检测音频文件的采样率
    sample_rate = get_sample_rate(audio_file_path)

    # 读取音频文件
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    # 将音频数据编码为base64
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="zh-CN",
        enable_word_time_offsets=True,  # 启用时间戳
        enable_automatic_punctuation=True  # 启用自动标点符号
    )

    # 调用 API 进行语音识别
    response = client.recognize(config=config, audio=audio)

    return response

def create_srt_subtitles(response, output_file="subtitles.srt", max_chars=40, max_duration=4.0):
    srt_counter = 1
    srt_content = ""

    for result in response.results:
        alternative = result.alternatives[0]
        words_info = alternative.words

        block_start_time = words_info[0].start_time.total_seconds()
        block_end_time = block_start_time
        block_text = ""
        block_duration = 0.0

        for i, word_info in enumerate(words_info):
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()

            block_duration += end_time - start_time

            # 根据标点符号或最大字符数/时间创建新字幕块
            block_text += word_info.word
            if (len(block_text) >= max_chars or word_info.word in "，。！？" or block_duration > max_duration):
                block_end_time = end_time
                block_start_time_str = f"{int(block_start_time // 3600):02}:{int((block_start_time // 60) % 60):02}:{int(block_start_time % 60):02},{int((block_start_time % 1) * 1000):03}"
                block_end_time_str = f"{int(block_end_time // 3600):02}:{int((block_end_time // 60) % 60):02}:{int(block_end_time % 60):02},{int((block_end_time % 1) * 1000):03}"

                srt_content += f"{srt_counter}\n{block_start_time_str} --> {block_end_time_str}\n{block_text.strip()}\n\n"
                srt_counter += 1

                block_start_time = end_time
                block_text = ""
                block_duration = 0.0

    # 写入最后一个块（防止遗漏）
    if block_text:
        block_start_time_str = f"{int(block_start_time // 3600):02}:{int((block_start_time // 60) % 60):02}:{int(block_start_time % 60):02},{int((block_start_time % 1) * 1000):03}"
        block_end_time_str = f"{int(block_end_time // 3600):02}:{int((block_end_time // 60) % 60):02}:{int(block_end_time % 60):02},{int((block_end_time % 1) * 1000):03}"

        srt_content += f"{srt_counter}\n{block_start_time_str} --> {block_end_time_str}\n{block_text.strip()}\n\n"

    with open(output_file, "w") as f:
        f.write(srt_content)

    print(f"字幕文件已生成: {output_file}")


# 使用示例
audio_file_path = "segment_0_30.wav"
mono_audio_file_path = "extracted_audio_mono.wav"

# 转换为单声道
convert_to_mono(audio_file_path, mono_audio_file_path)

# 进行语音识别
response = transcribe_audio(mono_audio_file_path)
create_srt_subtitles(response)

