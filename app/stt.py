import os
import io
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech

# Google Cloud 및 OpenAI API 키 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"app\stt\robust-summit-425707-d7-62176ec3f4d7.json"

# ffmpeg 및 ffprobe 경로 설정
ffmpeg_path = r"app\stt\ffmpeg-2024-06-06-git-d55f5cba7b-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"app\stt\ffmpeg-2024-06-06-git-d55f5cba7b-essentials_build\bin\ffprobe.exe"

# 환경 변수에 ffmpeg 및 ffprobe 경로 추가
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# pydub의 ffmpeg 및 ffprobe 경로 설정
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def convert_to_wav(file_path):
    try:
        print(f"Converting {file_path} to WAV format using ffmpeg at {AudioSegment.converter}.")
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_channels(1)  # 오디오를 모노로 변환
        wav_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        print(f"Converted file saved to: {wav_path}")
        return wav_path
    except Exception as e:
        print(f"Error during conversion: {e}")
        raise e

def long_running_recognize(file_path):
    print(f"Starting long running speech recognition for file: {file_path}")
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ko-KR",
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=3600)  # 최대 1시간 대기

    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)

    return "\n".join(transcripts)

def process_audio_file(input_file_path):
    if not os.path.exists(input_file_path):
        return f"File not found: {input_file_path}"
    else:
        try:
            print(f"File found: {input_file_path}")
            wav_file_path = convert_to_wav(input_file_path)
            transcript = long_running_recognize(wav_file_path)
            print("Transcript:")
            print(transcript)
            return transcript
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

if __name__ == "__main__":
    # input_file_path = r"app\stt\test1.m4a"  # 여기에 변환할 m4a 파일 경로를 입력하세요.
    pass  # 테스트 시 직접 경로를 입력하는 부분은 제외
