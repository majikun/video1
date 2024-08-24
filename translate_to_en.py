from google.cloud import translate_v2 as translate
import os
import re

def parse_srt_for_subtitles(srt_file):
    """Parses the SRT file and returns a list of subtitles."""
    with open(srt_file, 'r', encoding="utf-8") as file:
        content = file.read()
    
    pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        start_time = match[0]
        end_time = match[1]
        text = match[2].replace('\n', ' ').strip()
        subtitles.append((start_time, end_time, text))
    
    return subtitles

def translate_subtitles(subtitles, target_language='en'):
    """Translates a list of subtitles using Google Cloud Translation API."""
    translate_client = translate.Client()

    translated_subtitles = []
    for start_time, end_time, text in subtitles:
        translation = translate_client.translate(text, target_language=target_language)
        translated_text = translation['translatedText']
        translated_subtitles.append((start_time, end_time, translated_text))

    return translated_subtitles

def save_translated_srt(translated_subtitles, output_srt_file):
    """Saves the translated subtitles back to an SRT file."""
    with open(output_srt_file, 'w', encoding='utf-8') as file:
        for i, (start_time, end_time, text) in enumerate(translated_subtitles):
            file.write(f"{i+1}\n")
            file.write(f"{start_time} --> {end_time}\n")
            file.write(f"{text}\n\n")

def main():
    srt_file_path = 'corrected_output_subtitle.srt'
    output_srt_file = 'translated_subtitle_full_en.srt'

    # 解析原始SRT文件
    subtitles = parse_srt_for_subtitles(srt_file_path)

    # 翻译字幕
    translated_subtitles = translate_subtitles(subtitles, target_language='en')

    # 保存翻译后的字幕到新的SRT文件
    save_translated_srt(translated_subtitles, output_srt_file)

    print(f"Translated SRT file saved as {output_srt_file}")

if __name__ == "__main__":
    main()
