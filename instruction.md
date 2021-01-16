curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.scorer
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.pbmm


## Append PYTHONPATH env variable with your custom Connector

export PYTHONPATH=/Users/{your_home_folder}/{url_to_project}/custom_components/:$PYTHONPATH

## Start bot
rasa run --cors "*" --debug --enable-api -p 5005
python3 -m http.server 8888

