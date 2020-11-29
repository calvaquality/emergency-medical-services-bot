## Download models for SST

curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.scorer
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.pbmm

## Download TTS (from Mozilla) and install

brew install pkg-config
git clone https://github.com/mozilla/TTS.git
git checkout origin/Tacotron2-iter-260K-824c09
cd TTS
python setup.py develop



## Downloading models for Mozilla TTS
https://drive.google.com/drive/folders/1GU8WGix98WrR3ayjoiirmmbLUZzwg4n0

## Problem with building dependency for Matplotlib (freetype2)
https://github.com/matplotlib/matplotlib/issues/3029/
brew install freetype

## Fixing problem with compilation (clang returned error 1)
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select -s /Applications/Xcode.app

## Fixing problem with libsndfile (package not found)
brew install libsndfile