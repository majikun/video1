import re
from googletrans import Translator

def parse_srt(srt_file):
    """Parses the SRT file and returns a list of tuples (index, start_time, end_time, text)."""
    with open(srt_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        index = match[0]
        start_time = match[1]
        end_time = match[2]
        text = match[3].replace('\n', ' ').strip()
        subtitles.append((index, start_time, end_time, text))
    
    return subtitles

def translate_text(text, target_language='en'):
    """Translates the given text to the target language."""
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

def translate_srt(srt_file, output_file):
    """Translates the SRT file to English and saves the output to a new file."""
    subtitles = parse_srt(srt_file)
    translated_subtitles = []

    for index, start_time, end_time, text in subtitles:
        translated_text = translate_text(text)
        translated_subtitles.append((index, start_time, end_time, translated_text))

    with open(output_file, 'w', encoding='utf-8') as file:
        for index, start_time, end_time, text in translated_subtitles:
            file.write(f"{index}\n{start_time} --> {end_time}\n{text}\n\n")

# Usage
srt_file_path = 'corrected_output_subtitle.srt'
translated_srt_file = 'translated_output_subtitle.srt'
translate_srt(srt_file_path, translated_srt_file)
