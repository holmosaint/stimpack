import subprocess
import signal
import socket
import numpy as np
import serial
import time
from threading import Thread

from stimpack.device.locomotion.loco_managers import LocoManager, LocoClosedLoopManager

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 33335         # The port used by the server
# Specify the port and the baud rate (must match the settings in the Arduino code)
ARDUINO_PORT = '/dev/ttyACM0'  # Change this to your Arduino port
BAUD_RATE = 57600       # Must match the baud rate in the Arduino code

class ArduinoManager(LocoManager):
    def __init__(self, host=HOST, port=PORT, arduino_port=ARDUINO_PORT, baud_rate=BAUD_RATE, start_at_init=True, verbose=False):
        super().__init__(verbose=verbose)
        
        self.host = host
        self.port = port
        self.arduino_port = arduino_port
        self.baud_rate = baud_rate

        self.started = False
        self.p = None

        if start_at_init:
            self.start()

    def start(self):
        if self.started:
            if self.verbose: print("ArduinoManager: ArduinoManager is already running.")
        else:
            self.p = subprocess.Popen(["python", "arduinotrac.py", 
                                       f"{self.host}", f"{self.port}", f"{self.arduino_port}", f"{self.baud_rate}"],
                                      start_new_session=True)
            self.started = True

    def close(self, timeout=5):
        if self.started:
            self.p.send_signal(signal.SIGTERM)
            
            try:
                self.p.wait(timeout=timeout)
            except:
                print("KeytracManager: Timeout expired for closing Keytrac. Killing process...")
                self.p.kill()
                self.p.terminate()

            self.p = None
            self.started = False
        else:
            if self.verbose: print("ArduinoManager: ArduinoManager hasn't been started yet. Cannot be closed.")

class ArduinoClosedLoopManager(LocoClosedLoopManager):
    def __init__(self, stim_server, host=HOST, port=PORT, 
                       arduino_port=ARDUINO_PORT, baud_rate=BAUD_RATE, 
                       start_at_init=False, udp=True):
        super().__init__(stim_server=stim_server, host=host, port=port, save_directory=None, start_at_init=False, udp=udp)
        print('start creating arduino...')
        self.ad_manager = ArduinoManager(host=HOST, port=PORT, arduino_port=arduino_port, baud_rate=baud_rate, start_at_init=False)

        print('get started!')
        if start_at_init:    self.start()

    def start(self):
        super().start()
        self.ad_manager.start()

    def close(self):
        super().close()
        self.ad_manager.close()

    def _parse_line(self, line):
        toks = line.split(", ")

        # Keytrac lines always starts with KT
        if toks.pop(0) != "AD":
            print(line)
            print('Bad read')
            return None
        
        x = float(toks[0])
        y = float(toks[1])
        z = float(toks[2])
        theta = np.rad2deg(float(toks[3]))
        phi = np.rad2deg(float(toks[4]))
        roll = np.rad2deg(float(toks[5]))
        ts = float(toks[6])

        return {'x': x, 'y': y, 'z':z, 'theta': theta, 'phi': phi, 'roll': roll, 'frame_num': 1, 'ts': ts}

    def set_pos_0(self, loco_pos = {'x': 0, 'y': 0, 'z': 0, 'theta': 0, 'phi': 0, 'roll': 0}, use_data_prev=True, get_most_recent=True, write_log=False):
        self.socket_manager.send_message("reset_pos")
        super().set_pos_0(loco_pos = {'x': 0, 'y': 0, 'z': 0, 'theta': 0, 'phi': 0, 'roll': 0}, 
                          use_data_prev=use_data_prev, 
                          get_most_recent=get_most_recent, 
                          write_log=write_log)
        