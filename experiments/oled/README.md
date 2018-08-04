Brynand was here!

## Setup on Raspberry Pi 3B

1. Follow instructions at https://github.com/cjacoby/robotwedding/blob/master/README.md
1. `sudo apt-get install libssl1.0-dev libjpeg-dev`
1. `pipenv install`

## Run
```pipenv run ./text.py --display ssd1351 --width 128 --height 128 --interface spi --spi-bus-speed 8000000```
