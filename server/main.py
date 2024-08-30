from flask import Flask, render_template, request
import json
import os

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
    
@app.route('/api/devices/input/<mac>/', methods=['PUT'])
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

@app.route('/api/devices/output/<mac>/', methods=['GET'])
def get_output(mac):
    if mac in output_device_pins:
        return output_device_pins[mac]
    else:
        return "Device with MAC address: " + mac + " not found"
    
app.run(debug=True,port=8080, host="0.0.0.0")