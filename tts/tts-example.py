from gtts import gTTS


def my_fnc():
    text = "Hello world"

    var = gTTS(text=text, lang='en')

    var.save('eng.mp3')


if __name__ == '__main__':
    my_fnc()
