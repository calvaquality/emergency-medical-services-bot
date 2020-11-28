import os
import wave

import numpy
import sounddevice as sd
from deepspeech import Model
from scipy.io.wavfile import write

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

WAVE_OUTPUT_FILENAME = "stt/example-sound.wav"


def record_audio(WAVE_OUTPUT_FILENAME):
    fs = 16000  # Sample rate
    seconds = 5  # Duration of recording

    print("* recording")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("* done recording")
    write(WAVE_OUTPUT_FILENAME, fs, myrecording)  # Save as WAV file


def deepspeech_predict(WAVE_OUTPUT_FILENAME):
    ds = Model('stt/deepspeech-0.9.1-models.pbmm')
    ds.enableExternalScorer('stt/deepspeech-0.9.1-models.scorer')
    inputAudioFile = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
    audio1 = numpy.frombuffer(inputAudioFile.readframes(inputAudioFile.getnframes()), numpy.int16)
    inputAudioFile.close()
    return ds.stt(audio1)

if __name__ == '__main__':
    record_audio(WAVE_OUTPUT_FILENAME)
    predicted_text = deepspeech_predict(WAVE_OUTPUT_FILENAME)
    print(predicted_text)
