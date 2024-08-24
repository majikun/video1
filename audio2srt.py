import json
import re

def parse_offset(offset_str):
    """Converts offset string (e.g., '0.200s') to seconds and nanoseconds."""
    if offset_str is None:
        return 0, 0  # Default value for missing offsets
    seconds = float(offset_str.replace('s', ''))
    whole_seconds = int(seconds)
    nanos = int((seconds - whole_seconds) * 1e9)
    return whole_seconds, nanos

def format_timestamp(seconds, nanos):
    """Formats time given in seconds and nanoseconds to SRT timestamp format."""
    total_seconds = seconds + nanos / 1e9
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

def clean_text(text):
    """Removes unwanted characters from the text."""
    return text.replace('▁', '').strip()

def split_transcript_by_punctuation(transcript):
    """Splits transcript by punctuation (Chinese and comma) while keeping punctuation attached to the sentence."""
    segments = re.split(r'([。！？，,])', transcript)
    segments = ["".join(pair) for pair in zip(segments[0::2], segments[1::2])]
    return segments

def convert_to_srt(json_data, output_srt_file):
    """Converts JSON data to SRT format."""
    srt_content = []
    idx = 1
    
    for result in json_data['results']:
        if 'words' in result['alternatives'][0]:
            words_info = result['alternatives'][0]['words']
            transcript = result['alternatives'][0]['transcript']

            # Split the transcript by punctuation
            text_segments = split_transcript_by_punctuation(transcript)
            
            segment_start_index = 0
            for segment in text_segments:
                segment_start_time = None
                segment_end_time = None
                segment_text = []

                for word_info in words_info[segment_start_index:]:
                    word = clean_text(word_info['word'])
                    start_offset = word_info.get('startOffset', "0s")
                    end_offset = word_info.get('endOffset', "0s")

                    start_seconds, start_nanos = parse_offset(start_offset)
                    end_seconds, end_nanos = parse_offset(end_offset)

                    if segment_start_time is None:
                        segment_start_time = (start_seconds, start_nanos)
                    segment_end_time = (end_seconds, end_nanos)

                    segment_text.append(word)
                    segment_start_index += 1

                    if word in segment:
                        break

                start_time_str = format_timestamp(*segment_start_time)
                end_time_str = format_timestamp(*segment_end_time)

                # Create the SRT block
                srt_content.append(f"{idx}")
                srt_content.append(f"{start_time_str} --> {end_time_str}")
                srt_content.append("".join(segment_text).strip())
                srt_content.append("")  # Blank line for SRT format

                idx += 1

    # Write to the SRT file
    with open(output_srt_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))

# Load JSON data from Google API
json_file_path = 'transcripts-extracted_audio_transcript_66c76096-0000-25bb-a936-582429bd7fb4.json'
output_srt_path = 'output_subtitle.srt'

with open(json_file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Convert JSON to SRT
convert_to_srt(json_data, output_srt_path)

print(f"SRT file created at: {output_srt_path}")
