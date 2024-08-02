import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

# setup pin 16 as an output pin
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)

# setup pin 32 as an output pin
GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)

input_proc = os.fork()

if input_proc > 0:
    while True:
        GPIO.output(16, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(16, GPIO.LOW)
        time.sleep(1)
    exit()

# output_proc = os.fork()

# if output_proc > 0:
#     while True:
#         GPIO.output(32, GPIO.HIGH)
#         time.sleep(1)
#         GPIO.output(32, GPIO.LOW)
#         time.sleep(1)
#     exit()

# wait for child processes to finish
os.waitpid(input_proc, 0)