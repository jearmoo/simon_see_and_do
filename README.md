# simon_see_and_do
A robot sees someone arrange blocks and it follows them.

The [IP Webcam App](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=en_US) feeds image data to the CV code.

## High Level Setup

Uses Python 3.6

### Mac
```
brew install zbar
```


### Ubuntu
```
sudo apt-get install libzbar-dev libzbar0
```

### Install Python Dependencies
```
pip install -r high_level_code/requirements.txt
```

## High Level Running
```
cd high_level_code
python led.py
python go.py
python see.py
