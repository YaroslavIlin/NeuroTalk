import pyaudio
import requests
import os
from get_iam_token import get_iam_token

from speechkit import SpeechSynthesis
from dotenv import load_dotenv

load_dotenv()


def synthesize(folder_id, iam_token, text):
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    headers = {
        "Authorization": "Bearer " + iam_token,
    }

    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": "oksana",
        "folderId": folder_id,
        "format": "lpcm",
        "sampleRateHertz": 48000,
    }

    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError(
                "Invalid response received: code: %d, message: %s"
                % (resp.status_code, resp.text)
            )

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


def pyaudio_play_audio_function(
    audio_data, num_channels=1, sample_rate=16000, chunk_size=4000
) -> None:
    """
    Воспроизводит бинарный объект с аудио данными в формате lpcm (WAV)

    :param bytes audio_data: данные сгенерированные спичкитом
    :param integer num_channels: количество каналов, спичкит генерирует
        моно дорожку, поэтому стоит оставить значение `1`
    :param integer sample_rate: частота дискретизации, такая же
        какую вы указали в параметре sampleRateHertz
    :param integer chunk_size: размер семпла воспроизведения,
        можно отрегулировать если появится потрескивание
    """
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=num_channels,
        rate=sample_rate,
        output=True,
        frames_per_buffer=chunk_size,
    )

    try:
        for i in range(0, len(audio_data), chunk_size):
            stream.write(audio_data[i : i + chunk_size])
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def get_synthesized_audio(text):
    token = get_iam_token()
    folder_id = os.getenv("CATALOG_ID")
    output = "speech.raw"
    with open(output, "wb") as f:
        for audio_content in synthesize(folder_id, token, text):
            f.write(audio_content)
    file_path = "speech.wav"

    if os.path.exists(file_path):
        os.remove(file_path)
    os.system("ffmpeg -f s16le -ar 48000 -ac 1 -i speech.raw speech.wav")


def play_audio(text, session):
    sample_rate = 16000  # частота дискретизации должна
    # совпадать при синтезе и воспроизведении
    synthesizeAudio = SpeechSynthesis(session)
    audio_data = synthesizeAudio.synthesize_stream(
        text=text, voice="oksana", format="lpcm", sampleRateHertz=sample_rate
    )
    # Воспроизводим синтезированный файл
    pyaudio_play_audio_function(audio_data, sample_rate=sample_rate)
