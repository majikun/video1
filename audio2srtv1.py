import json
import re

def format_timestamp(seconds, nanos):
    """Formats time given in seconds and nanoseconds to SRT timestamp format."""
    total_seconds = seconds + nanos / 1e9
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

def split_transcript_by_punctuation(transcript):
    """Splits transcript by punctuation (Chinese and comma) while keeping punctuation attached to the sentence."""
    segments = re.split(r'([。！？，,])', transcript)
    segments = ["".join(pair) for pair in zip(segments[0::2], segments[1::2])]
    return segments

def get_time_offset(word_info, key):
    """Safely get time offset from word_info dictionary, defaulting to time with zero seconds and nanoseconds if not present."""
    return word_info.get(key, {"seconds": 0, "nanos": 0})

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
                word_count = len(segment.strip())
                
                # Ensure we do not exceed the length of words_info
                if segment_start_index >= len(words_info):
                    break
                
                # Get the start and end time for this segment
                start_word = words_info[segment_start_index]
                end_word_index = min(segment_start_index + word_count - 1, len(words_info) - 1)
                end_word = words_info[end_word_index]
                
                start_time = get_time_offset(start_word, 'startTime')
                end_time = get_time_offset(end_word, 'endTime')
                
                start_time_str = format_timestamp(start_time['seconds'], start_time['nanos'])
                end_time_str = format_timestamp(end_time['seconds'], end_time['nanos'])
                
                # Create the SRT block
                srt_content.append(f"{idx}")
                srt_content.append(f"{start_time_str} --> {end_time_str}")
                srt_content.append(segment.strip())
                srt_content.append("")  # Blank line for SRT format
                
                # Update index and segment start index
                idx += 1
                segment_start_index += word_count

    # Write to the SRT file
    with open(output_srt_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))

# Load JSON data
json_file_path = 'transcripts-extracted_audio_transcript_66c76096-0000-25bb-a936-582429bd7fb4.json'
output_srt_path = 'output_subtitle.srt'

with open(json_file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Convert JSON to SRT
convert_to_srt(json_data, output_srt_path)

print(f"SRT file created at: {output_srt_path}")