import logging
import time
import uuid
import wave
from typing import Any
from typing import Optional, Text
from urllib import request

import numpy
from deepspeech import Model
from gtts import gTTS
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import OutputChannel
from rasa.core.channels.channel import UserMessage
from sanic import Blueprint
from sanic import response
from socketio import AsyncServer

logger = logging.getLogger(__name__)


class SocketBlueprint(Blueprint):
    def __init__(self, sio: AsyncServer, socketio_path, *args, **kwargs):
        self.sio = sio
        self.socketio_path = socketio_path
        super(SocketBlueprint, self).__init__(*args, **kwargs)

    def register(self, app, options):
        self.sio.attach(app, self.socketio_path)
        super(SocketBlueprint, self).register(app, options)


class SocketIOOutput(OutputChannel):

    @classmethod
    def name(cls):
        return "socketio"

    @staticmethod
    def convert_text_to_speech(sentence: Text, out_file_path: Text):
        text_to_speech = gTTS(text=sentence, lang='en')
        text_to_speech.save(out_file_path)
        return out_file_path

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

        print('[BOT MESSAGE] ' + response['text'])
        self.convert_text_to_speech(response['text'], out_file)

        await self.sio.emit(self.bot_message_evt, {'text': response['text'], "link": link}, room=socket_id)

    async def send_text_message(self, recipient_id: Text, message: Text, **kwargs: Any) -> None:
        """Send a message through this channel."""

        await self._send_audio_message(self.sid, {"text": message})


class SocketIOInput(InputChannel):
    """A socket.io input channel."""

    @classmethod
    def name(cls):
        return "socketio"

    @classmethod
    def from_credentials(cls, credentials):
        credentials = credentials or {}
        return cls(credentials.get("user_message_evt", "user_uttered"),
                   credentials.get("bot_message_evt", "bot_uttered"),
                   credentials.get("namespace"),
                   credentials.get("session_persistence", False),
                   credentials.get("socketio_path", "/socket.io"),
                   )

    def __init__(self,
                 user_message_evt: Text = "user_uttered",
                 bot_message_evt: Text = "bot_uttered",
                 namespace: Optional[Text] = None,
                 session_persistence: bool = False,
                 socketio_path: Optional[Text] = '/socket.io'
                 ):
        self.bot_message_evt = bot_message_evt
        self.session_persistence = session_persistence
        self.user_message_evt = user_message_evt
        self.namespace = namespace
        self.socketio_path = socketio_path
        self.speech_to_text_model = Model('stt/deepspeech-0.9.1-models.pbmm')
        self.speech_to_text_model.enableExternalScorer('stt/deepspeech-0.9.1-models.scorer')

    def blueprint(self, on_new_message):
        sio = AsyncServer(async_mode="sanic", logger=True, cors_allowed_origins='*')
        socketio_webhook = SocketBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        @socketio_webhook.route("/", methods=['GET'])
        async def health(request):
            return response.json({"status": "ok"})

        @sio.on('connect')
        async def connect(sid, environ):
            print("User {} connected to socketIO endpoint.".format(sid))

        @sio.on('disconnect')
        async def disconnect(sid):
            print("User {} disconnected from socketIO endpoint."
                  "".format(sid))

        @sio.on('session_request')
        async def session_request(sid, data):
            print('Session request received')

            if data is None:
                data = {}
            if 'session_id' not in data or data['session_id'] is None:
                data['session_id'] = uuid.uuid4().hex
            await sio.emit("session_confirm", data['session_id'], room=sid)
            print("User {} connected to socketIO endpoint."
                  "".format(sid))

        @sio.on('user_uttered')
        async def handle_message(sid, data):
            print('User uttered')
            output_channel = SocketIOOutput(sio, sid, self.bot_message_evt, data['message'])
            if data['message'] == "/get_started":
                message = data['message']
            else:
                ##receive audio
                received_file = 'output_' + sid + '.wav'

                request.urlretrieve(data['message'], received_file)

                # fs, audio = wav.read("output_{0}.wav".format(sid))
                input_audio_file = wave.open("output_{0}.wav".format(sid), 'rb')
                converted_audio_to_bytes = numpy.frombuffer(input_audio_file.readframes(input_audio_file.getnframes()),
                                                            numpy.int16)
                input_audio_file.close()
                message = self.speech_to_text_model.stt(converted_audio_to_bytes)

                await sio.emit(self.user_message_evt, {"text": message}, room=sid)

            message_rasa = UserMessage(message, output_channel, sid,
                                       input_channel=self.name())
            await on_new_message(message_rasa)

        return socketio_webhook
