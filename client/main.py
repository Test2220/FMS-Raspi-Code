import requests
from uuid import getnode
from time import sleep
import json
import os
import RPi.GPIO as GPIO
import signal

GPIO.setmode(GPIO.BCM)

# GPIO.setup(17, GPIO.OUT)
status_state = ""

server_ip = "10.0.100.21"
config_port = 8080
control_port = 8007

inputs = []
outputs = []

r_mac = getnode()
macAddr = ':'.join(("%012X" % r_mac)[i:i+2] for i in range(0, 12, 2))
my_pid = os.getpid()

def register_device(mac):
    response = requests.get("http://" + server_ip + ":" + str(config_port) + "/register/" + mac)
    return response.text

def get_config(mac):
    response = requests.get("http://" + server_ip + ":" + str(config_port) + "/config/" + mac)
    return response.json()

def setup():
    try:
        register_device(macAddr)
        print("Device registered")
    except ConnectionError:
        print("Could not connect to server")
        print("Retrying...")
        sleep(4)
        setup()
    except Exception as e:
        print(e)
        print("Retrying...")
        sleep(4)
        setup()

    try:
        config = get_config(macAddr)
        if "error" in config:
            print(config["error"])
            print("Retrying...")
            sleep(4)
            setup()
        else:
            print("Config received")
            return config
    except ConnectionError:
        print("Could not connect to server")
        print("Retrying...")
        sleep(4)
        setup()
    except Exception as e:
        print(e)
        print("Retrying...")
        sleep(4)
        setup()

config = setup()

print(config)

def config_pins(config):
    print("Configuring pins...")
    if "1" in config:
        for pin in config:
            if config[pin] == 1:
                # Set pin as output
                try:
                    o_pin = int(pin)
                    GPIO.setup(o_pin, GPIO.OUT)
                    print("Pin " + str(o_pin) + " set as output")
                    outputs.append(o_pin)
                except Exception as e:
                    print(e)
                    print("Pin error: " + str(pin))
                pass
            elif config[pin] == 2:
                # Set pin as input
                try:
                    i_pin = int(pin)
                    GPIO.setup(i_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                    print("Pin " + str(i_pin) + " set as input")
                    inputs.append(i_pin)
                except Exception as e:
                    print(e)
                    print("Pin error: " + str(pin))
                pass
            elif config[pin] == None or config[pin] == 0 or config[pin] == 4 or config[pin] == "none" or config[pin] == "None":
                # Set pin as none
                print("Pin " + str(pin) + " set as none")
                pass
            else:
                print("Invalid pin mode: " + str(config[pin]))
    else:
        print("No pins to configure")
        return Exception


def attempt_config(i_config):
    try:
        config_pins(i_config)
    except Exception:
        "Unable to configure pins. Retrying in 4.."
        sleep(4)
        attempt_config()

attempt_config(config)

def exit_handler():
    GPIO.cleanup()

def input_callback(channel):
    print("Input detected on pin " + str(channel))
     # Send input to server
    requests.get("http://" + server_ip + ":" + str(config_port) + "/api/devices/input/" + macAddr + "/", json={"pin": channel, "value": GPIO.input(channel)})

for pin in inputs:
    if pin in inputs:
        try :
            GPIO.add_event_detect(pin, GPIO.RISING, callback=input_callback)
            print("Event detect added for input pin " + str(pin))
        except Exception as e:
            print(e)
            print("Error adding event detect for pin " + str(pin))

if os.getpid() == my_pid:
    input_proc = os.fork()

if input_proc == 0:
    signal.signal(signal.SIGINT, exit_handler)
    signal.pause()



blinking_pins_fast = []
blinking_pins_slow = []
output_states = {}

for pin in outputs:
    output_states[str(pin)] = 0

def control_pin(pin, state):
    if output_states[str(pin)] == state:
        return
    if pin in blinking_pins_fast:
        blinking_pins_fast.remove(pin)
    if pin in blinking_pins_slow:
        blinking_pins_slow.remove(pin)
    if state == 0:
        GPIO.output(pin, GPIO.LOW)
        output_states[str(pin)] = 0
    elif state == 1:
        GPIO.output(pin, GPIO.HIGH)
        output_states[str(pin)] = 1
    elif state == 2:
        blinking_pins_slow.append(pin)
        output_states[str(pin)] = 2
    elif state == 3:
        blinking_pins_fast.append(pin)
        output_states[str(pin)] = 3

def poll_pin_states():
    try:
        req_url = "http://" + server_ip + ":" + str(config_port) + "/api/devices/output/" + macAddr + "/"
        response = requests.get(req_url)
        if response.status_code == 200:
            data = response.json()
            for pin in data:
                control_pin(pin, data[pin])
    except Exception as e:
        # print(e)
        print("Error polling pin states")
        print(response.json())
        return 0

if os.getpid() == my_pid:
    output_proc = os.fork()

if output_proc == 0:
    while True:
        if poll_pin_states() == 0:
            sleep(4)
        sleep(0.1)
    exit()

if os.getpid() == my_pid:
    blink_proc = os.fork()

def blink():
    iteration = 1
    while True:
        if iteration % 2 == 0:
            for pin in blinking_pins_fast:
                GPIO.output(pin, GPIO.HIGH)
        else:
            for pin in blinking_pins_fast:
                GPIO.output(pin, GPIO.LOW)
        if iteration <= 5 == 0:
            for pin in blinking_pins_slow:
                GPIO.output(pin, GPIO.HIGH)
        else:
            for pin in blinking_pins_slow:
                GPIO.output(pin, GPIO.LOW)
        if iteration == 10:
            iteration = 1
        else:
            iteration += 1
        sleep(0.2)

if blink_proc == 0:
    blink()
    exit()