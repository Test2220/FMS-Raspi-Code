import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(3, GPIO.OUT, initial=GPIO.HIGH) # Set pin 8 to be an output pin and set initial value to low (off)]
while True:
    GPIO.output(3, GPIO.LOW) # Turn on
    sleep(1) # Sleep for 1 second
    GPIO.output(16, GPIO.HIGH) # Turn off
    sleep(1) # Sleep for 1 second