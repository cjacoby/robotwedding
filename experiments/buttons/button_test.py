import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering

SELECT_PIN = 21

GPIO.setup(SELECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
#GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def button_callback(channel):
    print("Button {} was pushed!".format(channel))

GPIO.add_event_detect(SELECT_PIN, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge
#GPIO.add_event_detect(11, GPIO.RISING, callback=button_callback) # Setup event on pin 0 rising edge
#GPIO.add_event_detect(13, GPIO.RISING, callback=button_callback) # Setup event on pin 0 rising edge

message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up
