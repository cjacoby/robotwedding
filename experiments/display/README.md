Brynand was here!

## Setup on Raspberry Pi 3B

1. Follow instructions at https://github.com/cjacoby/robotwedding/blob/master/README.md
1. `sudo apt-get install libssl1.0-dev libjpeg-dev`
1. `pipenv install`

## Run with SSD1351 OLED
```pipenv run ./text.py --config=oled.config```

### Pins

| Display (top) | Display (bottom) | Raspberry Pi | 
|---------------|------------------|--------------| 
| SI            | MOSI             | MOSI         | 
| CL            | SCK              | SCLK         | 
| DC            | DC               | #24          | 
| R             | RESET            | #25          | 
| OC            | OLEDCS           | CE0          | 
| +             | Vin              | 5.0V         | 
| G             | GND              | GND          | 


## Run with ST7735 LCD
```pipenv run ./text.py --config=lcd.config```

### Pins
| Display (top) | Display (bottom) | Raspberry Pi | 
|---------------|------------------|--------------| 
| Vin           | Vin              | 3V3          | 
| Gnd           | GND              | GND          | 
| SCK           | SCK              | SCLK         | 
| SI            | MOSI             | MOSI         | 
| TCS           | TFT_CS           | CE0          | 
| RST           | RESET            | #24          | 
| D/C           | D/C              | #23          | 
| Lite          | LITE             | #18          | 
