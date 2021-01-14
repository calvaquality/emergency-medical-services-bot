curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.scorer
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.pbmm


## Start bot
rasa run --enable-api -p 5005
rasa run actions --actions demo.actions
python3 -m http.server 8888

