#import STMprotocol
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import time

import serial
import struct
import datetime
import time

class STMprotocol:
    def __init__(self, serial_port):
        self.ser = serial.Serial(serial_port, 64000, timeout=0.2)
        self.pack_format = {
            0x01: "=BBBB",
            0x03: "=Bf",
            0x04: "=B",
            0x05: "=B",
            0x06: "=Bffff",
            0x07: "=B",
            0x08: "=fff",
            0x09: "=",
            0x0a: "=",
            0x0b: "=BH",
            0x0c: "=B",
            0x0d: "=B",
            0x0e: "=fff",
            0x0f: "=",            
            0xa0: "=",
            0xa1: "=B",
            0xb0: "=B",
            0xb1: "=B",
            0xb2: "=BB",
            0xb3: "=B",
            0xb4: "=B",
            0xb5: "=B",
            0xa2: "=ffffff",

        }

        self.unpack_format = {
            0x01: "=BBBB",
            0x03: "=BB",
            0x04: "=BB",
            0x05: "=BB",
            0x06: "=BB",
            0x07: "=ffff",
            0x08: "=BB",
            0x09: "=fff",
            0x0a: "=fff",
            0x0b: "=BB",
            0x0c: "=f",
            0x0d: "=BB",
            0x0e: "=BB",
            0x0f: "=fff",
            0xa0: "=B",
            0xa1: "=B",
            0xb0: "=BB",
            0xb1: "=BB",
            0xb2: "=BB",
            0xb3: "=BB",
            0xb4: "=BB",
            0xb5: "=BB",
            0xa2: "=BB",
        }

    def send_command(self, cmd, args):
        # Clear buffer
        #print(self.ser.read(self.ser.in_waiting))
        
        parameters = bytearray(struct.pack(self.pack_format[cmd], *args))
        #print(parameters)
        msg_len = len(parameters) + 5
        msg = bytearray([0xfa, 0xaf, msg_len, cmd]) + parameters
        crc = sum(msg) % 256
        msg += bytearray([crc])

        #print("send ", repr(msg))
        self.ser.write(msg)

        start_time = datetime.datetime.now()
        time_threshold = datetime.timedelta(seconds=1)
        dt = start_time - start_time
        
        time.sleep(0.001)
        data = self.ser.read()[0]
        while (data != 0xfa) and (dt < time_threshold):
            data = self.ser.read()[0]

            current_time = datetime.datetime.now()
            dt = start_time - current_time

        adr = self.ser.read()[0]
        answer_len = self.ser.read()[0]
        answer = bytearray(self.ser.read(answer_len - 3))
        #print("answer ", repr(bytearray([data, adr, answer_len]) + answer))

        args = struct.unpack(self.unpack_format[cmd], answer[1:-1])
        return args

class Greenhouse():
    stm_order = ["temperature","humidity","luminosity"]
    stm_get_command = [0x0F, []]
    def __init__(self, serial_port, read_time_interval_seconds=1):
        self.port = serial_port
        self.protocol = STMprotocol(self.port)
        #self.protocol = None
        self.read_time_interval = read_time_interval_seconds
        self.params = {
            'temperature' : 0,
            'humidity' : 0,
            'luminosity' : 0
        }
        self.goal_params = {
            'temperature': None,
            'humidity' : None,
            'luminosity' : None
        }
        self.history = []
        self.logfile = open("history"+str(time.time())+'.txt',"w+")
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update_params,'interval',seconds=self.read_time_interval)
        
    def convert_stm_return_to_dict(self, stm_array):
        return {param:value for param, value in zip(self.stm_order,stm_array)}
            
    def update_params(self, log=True):
        self.params = self.convert_stm_return_to_dict(self.protocol.send_command(*self.stm_get_command))
        if log:
            self.history.append((time.time(), self.params))
            self.logfile.write(str(time.time()) + ' ')
            print(time.time(),end=' ')
            for key in self.stm_order:
                self.logfile.write(str(self.params[key]) + ' ')
                print(self.params[key],end=' ')
            print('')
            self.logfile.write('\n')
            self.logfile.flush()
            
    def get_params(self):
        return self.params
    
    def set_goal_params(self, new_params):
        self.goal_params.update(new_params)
        #
    
    def start(self):
        self.scheduler.start()
    
    def stop(self):
        self.scheduler.shutdown()
