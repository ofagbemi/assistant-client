import requests
import pyaudio
import wave
import sys
import os

from gtts import gTTS
from time import sleep
from select import select
from threading import Thread

import settings


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = 'file.wav'

audio = pyaudio.PyAudio()

recording = False

def play_file(path):
    os.system('mpg321 ' + path)

def wait_for_recording():
    play_file('assets/in.mp3')
    sleep(RECORD_SECONDS)
    global recording
    recording = False
    play_file('assets/out.mp3')

def write_audio_file(frames):
    wav_file = wave.open(OUTPUT_FILENAME, 'wb')
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(audio.get_sample_size(FORMAT))
    wav_file.setframerate(RATE)
    wav_file.writeframes(b''.join(frames))
    wav_file.close()

    print('wrote file to ', OUTPUT_FILENAME)
    return OUTPUT_FILENAME

def record():
    global recording
    recording = False
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    print('recording audio')
    recording = True

    Thread(target=wait_for_recording).start()

    frames = []
    while recording:
        frames.append(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()

    return frames

def get_audio_answer(path):
    response = requests.post(
        settings.API_URL,
        files={'audio': open(path, 'rb')}
    )
    json = response.json()
    answer = json.get('answer')

    if answer and len(answer) < 600:
        return answer
    return 'There was an error'

while True:
    input('press enter to record')
    frames = record()
    out_file = write_audio_file(frames)

    play_file('assets/searching.mp3')
    answer = get_audio_answer(out_file)

    tts = gTTS(text=answer, lang='en')
    tts.save('answer.mp3')
    play_file('answer.mp3')
