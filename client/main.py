import RPi.GPIO as GPIO
import socket

# GPIO Config
# Set the mode to use physical pin numbers
GPIO.setmode(GPIO.BOARD)

# Import JSON pin configuration
# File is at ./pin-config.py
# { "pin1": 3 }
# Uses physical pin numbers

# 0 = None
# 1 = Coil/Output
# 2 = Input
# 3 = Analog Output (see note below)
# 4 = Unused GPIO Pins

# Only physical pin 12 has analog output capabilities

# register with command and control server
# control server ip = 10.0.100.20/8007
ip_control = "10.0.100.20"
port_control = 8007

# ping server to check status
def ping_server():
    # Create a socket object
    s = socket.socket()
    # Get local machine name
    host = socket.gethostname()
    # Connect to the server
    s.connect((host, port_control))
    # Receive no more than 1024 bytes
    msg = s.recv(1024)
    print(msg.decode('ascii'))
    # Close the socket
    s.close()

# register with server
def register():
    # Create a socket object
    s = socket.socket()
    # Get local machine name
    host = socket.gethostname()
    # Connect to the server
    s.connect((host, port_control))
    # Receive no more than 1024 bytes
    msg = s.recv(1024)
    print(msg.decode('ascii'))
    # Close the socket
    s.close()

