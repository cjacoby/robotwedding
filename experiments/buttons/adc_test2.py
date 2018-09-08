# Importing modules
import mcp2008

from numpy import interp    # To scale values
from time import sleep    # To add delay
import RPi.GPIO as GPIO    # To use GPIO pins


# Initializing LED pin as OUTPUT pin
#led_pin = 20
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(led_pin, GPIO.OUT)

# Creating a PWM channel at 100Hz frequency
#pwm = GPIO.PWM(led_pin, 100)
#pwm.start(0)

# Read MCP3008 data
#def analogInput(channel):
#    adc = spi.xfer2([1,(8+channel)<<4,0])
#    data = ((adc[1]&3) << 8) + adc[2]
#    return data

# Below function will convert data to voltage
#def Volts(data):
#    volts = (data * 3.3) / float(1023)
#    volts = round(volts, 2) # Round off to 2 decimal places
#    return volts

#while True:
#    output = analogInput(0) # Reading from CH0
#    scaled_output = interp(output, [0, 1023], [0, 100])
#    temp_volts = Volts(output)
#    print(output, scaled_output, temp_volts)
#    pwm.ChangeDutyCycle(output)
#    sleep(0.1)

with mcp3008.MCP3008() as adc:
    print(adc.read([mcp3008.CH1]))
