import serial
import struct
import datetime
import time

class STMprotocol:
    stm_name = "/dev/ttyUSB0"
    pack_format = {
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
    unpack_format = {
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
    def __init__(self, serial_port):
        self.ser = serial.Serial(serial_port, 64000, timeout=0.2)

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
        
        time.sleep(0.02)
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
