Brynand was here!

## Setup on Raspberry Pi 3B

1. Follow instructions at https://github.com/cjacoby/robotwedding/blob/master/README.md
1. `sudo apt-get install libssl1.0-dev libjpeg-dev`
1. `pipenv install`

## Run with SSD1351 OLED
```pipenv run ./text.py --config=oled.config```

## Run with ST7735 LCD
```pipenv run ./text.py --config=lcd.config```
