import requests

# def writePin(pin, location, value):
#     if location in config["device_config"]:
#         device_mac = None
#         for device in output_device_pins:
#             if location in output_device_pins[device]:
#                 device_mac = device
#         if device_mac is None:
#             return "No device with location: " + location
#         if pin in output_device_pins[device_mac]:
#             output_device_pins[device_mac][pin] = value
#             return "Pin set"
#         else:
#             return "Pin not found"
        
url = "http://localhost:8080/"

locations_raw = requests.get("url" + "api/locations/")
locations = locations_raw.json()

devices_raw = requests.get("url" + "api/devices/")
devices = devices_raw.json()

def writePin(pin, location, value):
    device = None
    for dev in devices:
        if dev["location"] == location:
            device = dev
    if device is None:
        return "No device with location: " + location
    if pin in device["pins"]:
        requests.patch
        return "Pin set"
    else:
        return "Pin not found"