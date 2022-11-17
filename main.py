from moviepy.editor import *
from pytube import YouTube
import os
import boto3
import requests
import time

API_key= 'AQVN3V-ylMoGU1_bn40Lpai6_MgejNvqhblK_KLo'
key_id = 'YCAJEf_H4Vp2qEircTSe_-99t'
secret_key = 'YCMQO-IWCX8zJvg-LFrhCWKGC_UeEcgtp1BpPfsS'


def work_with_backet(action: str, audio: str):
    storage_url = "https://storage.yandexcloud.net"
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url=storage_url,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        region_name='ru-central1'
    )
    if action == "send":
        s3.upload_file(audio, 'python', audio)
    elif action == "delete":
        s3.delete_objects(Bucket='python', Delete={'Objects': [{'Key': audio}]})


def download_video(url: str) -> str:
    url = url.replace("watch?v=", "")
    yt = YouTube(url=url)
    name = yt.title.replace("/", "").replace("\\", "").replace("'", "").replace('"', '')
    yt.streams[2].download(filename=f'{name}.mp4')
    return f'{name}.mp4'


def convert_to_mp3(filename: str) -> str:
    file_name = filename[:-4]
    audioClip = AudioFileClip(filename)
    audioClip.write_audiofile(f"{file_name}.mp3", buffersize=50000)
    os.remove(f"{file_name}.mp4")
    return f'{file_name}.mp3'


def transcribe_audio(audio):
    file_link = f'https://storage.yandexcloud.net/python/{audio}'
    url_transcribe = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"
    body = {
        "config": {
            "specification": {
                "languageCode": "ru-RU",
                "model": "general",
                "audioEncoding": "MP3",
            }
        },
        "audio": {
            "uri": file_link
        }
    }
    print("Работает нейронка яндекса")
    header = {'Authorization': f'Api-Key {API_key}'}
    req = requests.post(url_transcribe, headers=header, json=body)
    data = req.json()
    id_operation = data['id']
    step = 15
    tt = 0

    while True:
        time.sleep(step)
        tt += step
        url_get = f"https://operation.api.cloud.yandex.net/operations/" + str(id_operation)
        req = requests.get(url_get, headers=header)
        req = req.json()
        if req['done']:
            break
        print(f"Ожидаем нейронку {str(tt)} секунд")
    print(f"Нейронка закончила")

    with open(f'{audio[:-4]}.txt', 'w') as f:
        for alternativites in req['response']['chunks']:
            if alternativites['channelTag'] == str(1):
                f.write(alternativites['alternatives'][0]['text'] + '. ')


def main():
    video = download_video(input("Enter URL:\n"))
    audio = convert_to_mp3(video)
    work_with_backet('send', audio)
    transcribe_audio(audio)
    os.remove(audio)
    work_with_backet('delete', audio)


if __name__ == '__main__':
    main()
