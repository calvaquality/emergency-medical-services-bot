import scipy.io.wavfile as wav
import sounddevice as sd
from deepspeech import Model
from scipy.io.wavfile import write

WAVE_OUTPUT_FILENAME = "test_audio.wav"


def record_audio(WAVE_OUTPUT_FILENAME):
    fs = 16000  # Sample rate
    seconds = 5  # Duration of recording

    print("* recording")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("* done recording")
    write(WAVE_OUTPUT_FILENAME, fs, myrecording)  # Save as WAV file


def deepspeech_predict(WAVE_OUTPUT_FILENAME):
    ds = Model('deepspeech-0.9.1-models.pbmm')

    audio = wav.read(WAVE_OUTPUT_FILENAME)
    return ds.stt(audio)


if __name__ == '__main__':
    record_audio(WAVE_OUTPUT_FILENAME)
    predicted_text = deepspeech_predict(WAVE_OUTPUT_FILENAME)
    print(predicted_text)
