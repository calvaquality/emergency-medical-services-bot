import time
from typing import Any, Text

from gtts import gTTS
from rasa.core.channels.channel import OutputChannel


class SocketIOOutput(OutputChannel):

    @classmethod
    def name(cls):
        return "socketio"

    def __init__(self, sio, sid, bot_message_evt, message):
        self.sio = sio
        self.sid = sid
        self.bot_message_evt = bot_message_evt
        self.message = message

    async def _send_audio_message(self, socket_id: Text, response: Any, **kwargs: Any) -> None:
        """Sends a message to the recipient using the bot event."""

        ts = time.time()
        out_file = str(ts) + '.wav'
        link = "http://localhost:8888/" + out_file

        self.convert_text_to_speech((response['text'], out_file))

        await self.sio.emit(self.bot_message_evt, {'text': response['text'], "link": link}, room=socket_id)

    async def send_text_message(self, recipient_id: Text, message: Text, **kwargs: Any) -> None:
        """Send a message through this channel."""

        await self._send_audio_message(self.sid, {"text": message})

    def convert_text_to_speech(self, sentence, OUT_FILE_PATH):
        text_to_speech = gTTS(text=sentence, lang='en')
        text_to_speech.save(OUT_FILE_PATH)
        return OUT_FILE_PATH
