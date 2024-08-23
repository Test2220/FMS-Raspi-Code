from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

json_config = open('config.json')
config = json.load(json_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devices')
def devices():
    return render_template('devices.html')

@app.route('/api/devices')
def api_devices():
    json_data = open('devices.json')
    data = json.load(json_data)
    return data

@app.route('/api/config/')
def api_config():
    return config

# If a client sends a MAC address, check if it is in the json file
@app.route('/register/<mac>')
def register(mac):
    json_data = open('devices.json')
    data = json.load(json_data)
    if mac in data:
        data[mac]["ip"] = request.remote_addr
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Registered IP address: " + request.remote_addr + " for MAC address: " + mac
    else:
        new_device = {
            mac: {
                "name": "Device",
                "ip": request.remote_addr,
                "location": "Unknown",
                "status": "Not Connected",
                "last_seen": "Never"
            }
        }
        data.update(new_device)
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Registering device with MAC address: " + mac + " and IP address: " + request.remote_addr

# If a client requests a config file, send it
@app.route('/config/<mac>')
def send_config(mac):
    json_device_data = open('devices.json')
    deviceData = json.load(json_device_data)
    if mac in deviceData:
        if deviceData[mac]["location"] != "Unknown":
            exists = os.path.exists(config["device_config"][deviceData[mac]["location"]])
            if not exists:
                return "Device config not found"
            device_config = json.load(open(config["device_config"][deviceData[mac]["location"]]))
            return device_config
        else:
            return {"error": "Location not set"}
    else:
        return {"error": "Device not found"}

# API endpoints for updating device data
@app.route('/api/devices/<mac>', methods=['DELETE'])
def remove_device(mac):
    json_data = open('devices.json')
    data = json.load(json_data)
    if mac in data:
        data.pop(mac)
        with open('devices.json', 'w') as f:
            json.dump(data, f)
        return "Device with MAC address: " + mac + " removed"
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
    
app.run(debug=True,port=8080, host="0.0.0.0")