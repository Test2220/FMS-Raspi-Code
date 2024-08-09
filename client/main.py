import requests
from uuid import getnode
from time import sleep
import json
import os
RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
status_state = ""

server_ip = "127.0.0.1"
config_port = 8080
control_port = 8007

inputs = []
outputs = []

r_mac = getnode()
macAddr = ':'.join(("%012X" % r_mac)[i:i+2] for i in range(0, 12, 2))

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
    if "pin1" in config:
        for pin in config:
            if config[pin] == 1:
                # Set pin as output
                o_pin = int(config[pin])
                GPIO.setup(o_pin, GPIO.OUT)
                print("Pin " + str(o_pin) + " set as output")
                inputs.append(o_pin)
                pass
            elif config[pin] == 2:
                # Set pin as input
                i_pin = int(config[pin])
                GPIO.setup(i_pin, GPIO.IN)
                print("Pin " + str(i_pin) + " set as input")
                outputs.append(i_pin)
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

# Spawn a process to handle input pins

proc_input = os.fork()

if proc_input == 0:
    print("Input process started")
    pin_states = {}
    new_states = {}
    # Update pin_states with current pin states and send to server if changed
    while True:
        for pin in inputs:
            # new_states[pin] = GPIO.input(pin)
            pass
        if new_states == {}:
            pass
        elif new_states != pin_states:
            print("Converting updated pin states to JSON...")
            # Use the template in templates/input.json to send the new pin states to the server
            t_inputs = open("templates/input.json")
            template = json.load(t_inputs)
            for pin in new_states:
                template[str(pin)] = new_states[pin]
            requests.post("http://" + server_ip + ":" + str(control_port) + "/api/input", json=template)
            pin_states = new_states
        new_states = {}
        sleep(0.1)