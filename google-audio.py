import os
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

MAX_AUDIO_LENGTH_SECS = 8 * 60 * 60

def run_batch_recognize():
    # Instantiates a client.
    client = SpeechClient()

    # The output path of the transcription result.
    gcs_output_folder = "gs://audio-0822/transcripts"

    # The name of the audio file to transcribe:
    audio_gcs_uri = "gs://audio-0822/audio-files/extracted_audio.wav"

    config = cloud_speech.RecognitionConfig(
        features=cloud_speech.RecognitionFeatures(
            enable_word_confidence=True,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
        ),
        language_codes=["cmn-Hans-CN"],
        model="long",
        explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,  # Correct enum for encoding
            sample_rate_hertz=44100,
            audio_channel_count=2
        )
    )

    output_config = cloud_speech.RecognitionOutputConfig(
        gcs_output_config=cloud_speech.GcsOutputConfig(uri=gcs_output_folder),
    )

    files = [cloud_speech.BatchRecognizeFileMetadata(uri=audio_gcs_uri)]

    request = cloud_speech.BatchRecognizeRequest(
        recognizer="projects/video-433305/locations/global/recognizers/_",
        config=config,
        files=files,
        recognition_output_config=output_config,
    )
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=30 * MAX_AUDIO_LENGTH_SECS)
    print(response)

run_batch_recognize()
