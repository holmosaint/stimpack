import sys
import socket
import time
import signal
import numpy as np
import os
import serial
from threading import Thread

from stimpack.util import ROOT_DIR

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 33335         # The port used by the server
# Specify the port and the baud rate (must match the settings in the Arduino code)
ARDUINO_PORT = '/dev/ttyACM0'  # Change this to your Arduino port
BAUD_RATE = 57600       # Must match the baud rate in the Arduino code

WHEEL_TICK_NO = 1024
WHEEL_R = (7.5/2) * 0.0254 # di = 7.5''
WHEEL_CIRC = 2*np.pi*WHEEL_R

class Arduino:
    def __init__(self, host=HOST, port=PORT, arduino_port=ARDUINO_PORT, baud_rate=BAUD_RATE, verbose=False):
        super().__init__()
        
        self.arduino_port = arduino_port
        self.baud_rate = baud_rate
        self.host = host
        self.port = port
        self.pos = {"x": 0, "y": 0, "z":0, "theta": 0, "phi": 0, "roll": 0}
        
        print('hello from arduino')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        print('hello from arduino again')
        self.sock.settimeout(0)
        
        self.ser = serial.Serial(self.arduino_port, self.baud_rate)
        
        self.receiving = True
        self.receive_thread = Thread(target=self.receive_loop)
        self.receive_thread.start()
        
        # self.send_thread = Thread(target=self.send_loop)
        # self.send_thread.start()
        
        # print(self.ser)
        
    def close(self):
        self.ser.close()
        
    def send_loop(self):
        while True:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8', errors='ignore').rstrip()
                print(line)
                if len(line) > 0:
                    self.send_state_message(line)
        
    def construct_state_message(self, line):
        timestamp = time.time()
        speed_scaler = WHEEL_CIRC / WHEEL_TICK_NO # 1e-2
        
        self.pos['y'] += float(line)*speed_scaler # TODO: change the speed for your purpose
        message = f"AD, " + \
                    f"{self.pos['x']}, {self.pos['y']}, {self.pos['z']}, {self.pos['theta']}, {self.pos['phi']}, {self.pos['roll']}, " + \
                    f"{timestamp}\n"
        return message

    def send_state_message(self, line):
        message = self.construct_state_message(line)

        try:
            self.sock.sendto(message.encode(), (self.host, self.port)) # UDP
        except:
            print("Failed to send message.")
            return
        # self.sock.sendall(message.encode()) # TCP

    def receive_message(self):
        # Receive a message from the receiver
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
        except socket.timeout as e:
            print(e)
            return
        except socket.error as e:
            # print(e)
            return

        if message == "reset_pos":
            self.reset_position()

    def receive_loop(self):
        while self.receiving:
            self.receive_message()

    def reset_position(self):
        self.pos = {"x": 0, "y": 0, "z":0, "theta": 0, "phi": 0, "roll": 0}
        

def main():
    host = HOST
    port = PORT
    relative_control = True
    verbose = False
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        arduino_port = sys.argv[3]
    if len(sys.argv) > 4:
        baud_rate = float(sys.argv[4])

    def signal_handler(sig, frame):
        print("Received SIGINT. Exiting...")
        arduino.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)

    arduino = Arduino(host=host, port=port, 
                      arduino_port=arduino_port, baud_rate=baud_rate)
    arduino.send_loop()

if __name__ == "__main__":
    main()