import os
import RPi.GPIO as GPIO
import time

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)

# setup pin 16 as an output pin
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)

# setup pin 32 as an output pin
GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)

input_proc = os.fork()

if input_proc == 0:
    while True:
        print(f"I am child process with PID {os.getpid()}")
    exit()

output_proc = os.fork()

if output_proc == 0:
    while True:
        print(f"I am child process with PID {os.getpid()}")
    exit()

while True:
        print(f"I am parent process with PID {os.getpid()}")
        print(f"Input PID: {input_proc}")
        print(f"Output PID: {output_proc}")
        time.sleep(10)