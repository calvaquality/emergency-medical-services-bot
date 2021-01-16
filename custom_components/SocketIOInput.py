import logging
import uuid
import wave
from typing import Optional, Text
from urllib import request

import numpy
from deepspeech import Model
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage
from sanic import response
from socketio import AsyncServer

from custom_components.SocketBlueprint import SocketBlueprint
from custom_components.SocketIOOutput import SocketIOOutput


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
        self.logger = logging.getLogger(__name__)
        self.speech_to_text_model = Model('stt/deepspeech-0.9.1-models.pbmm')
        self.speech_to_text_model.enableExternalScorer('stt/deepspeech-0.9.1-models.scorer')

    def blueprint(self, on_new_message):
        sio = AsyncServer(async_mode="sanic", cors_allowed_origins='*')
        socketio_webhook = SocketBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        @socketio_webhook.route("/", methods=['GET'])
        async def health(request):
            return response.json({"status": "ok"})

        @sio.on('connect', namespace=self.namespace)
        async def connect(sid, environ):
            self.logger.debug("User {} connected to socketIO endpoint.".format(sid))
            print('Connected!')

        @sio.on('disconnect', namespace=self.namespace)
        async def disconnect(sid):
            self.logger.debug("User {} disconnected from socketIO endpoint."
                              "".format(sid))

        @sio.on('session_request', namespace=self.namespace)
        async def session_request(sid, data):
            print('This is sessioin request')

            if data is None:
                data = {}
            if 'session_id' not in data or data['session_id'] is None:
                data['session_id'] = uuid.uuid4().hex
            await sio.emit("session_confirm", data['session_id'], room=sid)
            self.logger.debug("User {} connected to socketIO endpoint."
                              "".format(sid))

        @sio.on('user_uttered', namespace=self.namespace)
        async def handle_message(sid, data):

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
