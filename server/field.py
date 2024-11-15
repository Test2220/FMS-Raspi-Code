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
        
def writePin(pin, location, value):
    locations = requests.get()