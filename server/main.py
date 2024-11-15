from flask import Flask, render_template, request
import json, os, requests, logging, sys
from time import sleep
from multiprocessing import Queue
from threading import Thread

parent_pid = os.getpid()

# make a shared queue all processes can share
log_queue = Queue()

def printer():
    '''printer job running in parent process to actually print'''
    global log_queue
    while True:
        a, k=log_queue.get()
        print(*a, **k)

# make a thread to run printer to keep it in pid 1
Thread(target=printer).start()

# make a universal function all processes can log to
def mp_print(*a,**k):
    '''redirects print to pid 1's stdout'''
    global log_queue
    log_queue.put((a, k))
    
def mp_print_debug(*a, **k):
    ''' mp_print with pid info already cooked in '''
    mp_print(
        'pid={} ppid={}'.format(
            os.getpid(),
            os.getppid()
        ),
        *a,
        **k
    )

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

log.warning("This is a warning")
#create Flask app
app = Flask(__name__)

#create devices.json if it doesn't exist
try:
    # Create a new file called devices.json to store device data
    n_devices = open('devices.json', 'x')

    # Write an empty JSON object to the file
    n_devices.write("{}")

    # Close the file
    n_devices.close()
except FileExistsError:
    # If the file already exists, do nothing
    pass

# Load the config file
json_config = open('config.json')

# Parse the JSON data
config = json.load(json_config)


# Define the index route
@app.route('/')
def index():
    return render_template('index.html')

# Define the devices route
@app.route('/devices')
def devices():
    return render_template('devices.html')

# Define the devices api route
# This is used by the web interface to get device data
@app.route('/api/devices')
def api_devices():
    json_data = open('devices.json')
    data = json.load(json_data)
    return data

# Define the config route
# This is used by the web interface to get the config data,
# specifically the location options
@app.route('/api/config/')
def api_config():
    return config

# If a client sends a MAC address, check if it is in the json file
@app.route('/register/<mac>')
def register(mac):
    # Open the devices.json file
    json_data = open('devices.json')

    # Load the JSON data
    data = json.load(json_data)

    # Check if the MAC address is in the JSON data
    if mac in data:
        # If the MAC address is in the JSON data, update the IP address
        data[mac]["ip"] = request.remote_addr

        # Write the updated data to the file
        with open('devices.json', 'w') as f:
            json.dump(data, f)

        # Return a message to the client
        return "Registered IP address: " + request.remote_addr + " for MAC address: " + mac
    else:
        # If the MAC address is not in the JSON data, add it
        new_device = {
            mac: {
                "name": "Device",
                "ip": request.remote_addr,
                "location": "Unknown",
                "status": "Not Connected",
                "last_seen": "Never"
            }
        }

        # Update the JSON data with the new device
        data.update(new_device)

        # Write the updated data to the file
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Registering device with MAC address: " + mac + " and IP address: " + request.remote_addr

# If a client requests a config file, send it
@app.route('/config/<mac>')
def send_config(mac):
    # Open the devices.json file
    json_device_data = open('devices.json')

    # Load the JSON data
    deviceData = json.load(json_device_data)

    # Check if the MAC address is in the JSON data
    if mac in deviceData:
        # Check if the location is set
        if deviceData[mac]["location"] != "Unknown":
            # Check if the device config file exists
            exists = os.path.exists(config["device_config"][deviceData[mac]["location"]])
            if not exists:
                # If the device config file does not exist, return an error message
                return "Device config not found"
            # Load the device config file
            device_config = json.load(open(config["device_config"][deviceData[mac]["location"]]))

            # Return the device config
            return device_config
        else:
            # If the location is not set, return an error message
            return {"error": "Location not set"}
    else:
        # If the MAC address is not in the JSON data, return an error message
        return {"error": "Device not found"}

# API endpoints for updating device data
@app.route('/api/devices/<mac>', methods=['DELETE'])
def remove_device(mac):
    # Open the devices.json file
    json_data = open('devices.json')

    # Load the JSON data
    data = json.load(json_data)

    # Check if the MAC address is in the JSON data
    if mac in data:
        # Remove the device with the specified MAC address
        data.pop(mac)

        # Write the updated data to the file
        with open('devices.json', 'w') as f:
            json.dump(data, f)

        # Return a message to the client
        return "Device with MAC address: " + mac + " removed"
    else:
        # If the MAC address is not in the JSON data, return an error message
        return "Device with MAC address: " + mac + " not found"
    
@app.route('/api/devices/<mac>', methods=['PUT'])
def update_device(mac):
    # Open the devices.json file
    json_data = open('devices.json')

    # Load the JSON data
    data = json.load(json_data)

    # Check if the MAC address is in the JSON data
    if mac in data:
        # Update the device data
        data[mac]["location"] = request.json["location"]

        # Write the updated data to the file
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Location updated for device with MAC address: " + mac
    else:
        return "Device with MAC address: " + mac + " not found"

@app.route('/api/devices/location/<mac>', methods=['PUT'])
def update_location(mac):
    json_data = open('devices.json')
    data = json.load(json_data)
    if mac in data:
        data[mac]["location"] = request.json["location"]
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Location updated for device with MAC address: " + mac
    else:
        return "Device with MAC address: " + mac + " not found"
    
@app.route('/api/devices/input/<mac>/', methods=['POST'])
def update_input(mac):
    json_data = open('devices.json')
    data = json.load(json_data)
    if mac in data:
        try:
            device_file = open(mac + ".json", "x")
        except FileExistsError:
            device_file = open(mac + ".json")
        current_data = json.load(device_file)
        if request.json["pin"] in current_data:
            current_data[request.json["pin"]] = request.json["value"]
            with open(mac + ".json", 'w') as f:
                json.dump(current_data, f)
            return "Input state updated for device with MAC address: " + mac
        else:
            current_data.update({request.json["pin"]: request.json["value"]})
    else:
        return "Device with MAC address: " + mac + " not found"

output_device_pins = {}
def setup_output_pins():
    #open the devices.json file
    json_data = open('devices.json')

    #load the JSON data
    data = json.load(json_data)

    #loop through the data
    for device in data:
        if device in output_device_pins:
            continue
        output_device_pins[device] = {}
        device_pins = send_config(device)
        if "error" in device_pins:
            continue
        for pin in device_pins:
            if device_pins[pin] == 1:
                output_device_pins[device][pin] = 0
    return output_device_pins
setup_output_pins()

input_device_pins = {}
def setup_input_pins():
    #open the devices.json file
    json_data = open('devices.json')

    #load the JSON data
    data = json.load(json_data)

    #loop through the data
    for device in data:
        if device in input_device_pins:
            continue
        input_device_pins[device] = {}
        device_pins = send_config(device)
        if "error" in device_pins:
            continue
        for pin in device_pins:
            if device_pins[pin] == 2:
                input_device_pins[device][pin] = 0
    return input_device_pins
setup_input_pins()

try:
    # Create a new file called devices.json to store device data
    n_devices = open('outputs.json', 'x')

    # Write an empty JSON object to the file
    n_devices.write("{}")

    # Close the file
    n_devices.close()
except FileExistsError:
    # If the file already exists, do nothing
    pass


@app.route('/api/devices/output/<mac>/', methods=['GET'])
def get_output(mac):
    output_device_pins = json.load(open('outputs.json'))
    if mac in output_device_pins:
        return output_device_pins[mac]
    else:
        return "Device with MAC address: " + mac + " not found"
    
@app.route('/api/devices/outputs/', methods=['GET'])
def get_outputs():
    output_device_pins = json.load(open('outputs.json'))
    return output_device_pins

@app.route('/api/devices/input/<mac>/', methods=['GET', 'PATCH'])
def get_input(mac):
    if mac in input_device_pins:
        if request.method == 'PATCH':
            print(input_device_pins)
            pin = str(request.json["pin"])
            value = request.json["value"]
            if pin in input_device_pins[mac]:
                input_device_pins[mac][pin] = value
            return "Input state updated for device with MAC address: " + mac
        else:
            return input_device_pins[mac]
    else:
        # if a location is given instead of a mac address
        if mac in config["device_config"]:
            location = mac
            devices_file = requests.get("http://localhost:8080/api/devices")
            devices = devices_file.json()
            device_mac = None
            for device in devices:
                if devices[device]["location"] == location:
                    device_mac = device
                    return get_input(device_mac)
            if device_mac is None:
                return "No device with location: " + mac
            return input_device_pins[device_mac]
        return "Device with MAC address: " + mac + " not found"

plcData = ""
ArenaState = ""
#api call to produce a json of the pinstate.
@app.route("/api/PLC", methods=['POST','GET'])
def PLCAPI():
   error = None
   global plcData 
   if request.method == 'POST':
      plcData = request.get_json(silent=False)
   return plcData
@app.route("/api/arena", methods=['POST','GET'])
def ArenaAPI():
   error = None
   global ArenaState 
   if request.method == 'POST':
      ArenaState = request.get_json(silent=False)
   return ArenaState
    
def readPin(pinObj):
    pin = pinObj["pin"]
    location = pinObj["location"]
    # make a request to my own api to get the pin state
    pin_state = requests.get("http://localhost:8080/api/devices/input/" + location + "/")
    return pin_state


def writePin(pin, location, value):
    if location in config["device_config"]:
        device_mac = None
        for device in output_device_pins:
            if location in output_device_pins[device]:
                device_mac = device
        if device_mac is None:
            return "No device with location: " + location
        if pin in output_device_pins[device_mac]:
            output_device_pins[device_mac][pin] = value
            return "Pin set"
        else:
            return "Pin not found"

def modifyPoints(redA=0, redT=0, redE=0, blueA=0, blueT=0, blueE=0):
    request_type = "PATCH"
    request_url = "http://172.16.20.5:8080/api/scores"
    request_data = {}
    if redA != 0:
        request_data["redA"] = redA
    if redT != 0:
        request_data["redT"] = redT
    if redE != 0:
        request_data["redE"] = redE
    if blueA != 0:
        request_data["blueA"] = blueA
    if blueT != 0:
        request_data["blueT"] = blueT
    if blueE != 0:
        request_data["blueE"] = blueE
    requests.request(request_type, request_url, json=request_data)

game_code_pid = os.fork()

# ----ONLY PUT STATIC VARIABLES HERE----
blue_raspi = "blue"
red_raspi = "red"

blue_amp_pin = 10
blue_spkr_pin = 11

blue_amp = {"pin": blue_amp_pin, "location": blue_raspi}
blue_spkr = {"pin": blue_spkr_pin, "location": blue_raspi}

red_amp_pin = 10
red_spkr_pin = 11

red_amp = {"pin": red_amp_pin, "location": red_raspi}
red_spkr = {"pin": red_spkr_pin, "location": red_raspi}
# ----END OF STATIC VARIABLES----

if game_code_pid == 0:
    while True:
        # ----PUT GAME PERIODIC CODE HERE----

        # blue_amp_state = readPin(blue_amp)
        # blue_spkr_state = readPin(blue_spkr)

        # red_amp_state = readPin(red_amp)
        # red_spkr_state = readPin(red_spkr)

        # if blue_amp_state == 1:
        #     modifyPoints(blueA=1)
        # if blue_spkr_state == 1:
        #     modifyPoints(blueA=2)
        # if red_amp_state == 1:
        #     modifyPoints(redA=1)
        # if red_spkr_state == 1:
        #     modifyPoints(redA=2)

        mp_print_debug("Game periodic code running")

        # ----END OF GAME PERIODIC CODE----
        sleep(0.1)
    
app.run(debug=True,port=8080, host="0.0.0.0")
