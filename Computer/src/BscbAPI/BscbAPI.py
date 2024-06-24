import serial
import serial.tools.list_ports
import struct
import time
from enum import Enum
from typing import List


class Status(Enum):
    overload = 0
    error = 1
    timeout = 2
    normal = 3
    idle = 8
    not_init = 9


class SensorID(Enum):
    LOAD = 0
    UNLOAD = 1
    BUFFER = 2
    SPARE = 3


class StarWheelTimer:
    def __init__(self) -> None:
        self.inited: bool = False
        self.index: int = 0
        self.timer: List[time.time] = [time.time()] * 80
        self.unloaded_count: List[int] = [0] * 80

    def is_inited(self):
        return self.inited

    def reset(self):
        self.inited: bool = True
        self.index: int = 0

    def move_index(self):
        self.index = (self.index + 1) % 80

    def update_slot(self):
        self.timer[self.index - 1] = time.time()
        self.unloaded_count[self.index - 1] += 1

    def is_it_overtime(self, timeout_s: int = 3600):
        return (time.time() - self.timer[self.index]) > timeout_s


class BScbAPI:
    BAUD_RATE = 115200
    DEVICE_NAME_LIST = ["Arduino Leonardo", "Arduino Leonardo (COM5)"]

    def __init__(self, port="", baud_rate=BAUD_RATE, ar_timeout=0.2) -> None:
        self.is_inited = False
        self.baud_rate = baud_rate
        self.timeout = ar_timeout
        self.star_wheel_status = Status.not_init
        self.unloader_status = Status.idle
        self.com_port = self.get_port() if port == "" else port
        self.timer = StarWheelTimer()
        print(f"Serial communication port: {self.com_port}")
        if self.com_port is not None:
            self.ser = serial.Serial(self.com_port, self.baud_rate, timeout=self.timeout)
            self.is_inited = True
        else:
            self.ser = None

    def __enter__(self):
        # self.ser = serial.Serial(self.com_port, self.baud_rate, timeout=self.timeout)
        return self

    def __exit__(self, *args, **kwargs):
        self.ser.close()
        return self

    def update_com_port(self):
        self.ser.close()
        self.com_port = self.get_port()
        print(f"Serial communication port: {self.com_port}")
        if self.com_port is not None:
            self.ser = serial.Serial(self.com_port, self.baud_rate, timeout=self.timeout)
            self.is_inited = True

    def is_com_ready(self):
        return self.is_inited

    def get_port(self):
        ports = serial.tools.list_ports.comports()
        if len(ports) > 0:
            for port in ports:
                if port.description in BScbAPI.DEVICE_NAME_LIST:
                    return port.device
        return None

    def close(self):
        self.ser.close()

    # ========================================= Responds ========================================= #

    def got_ACK_respond(self, timeout=3):
        time_out = time.time() + timeout
        while True:
            try:
                ack = self.ser.readline()
                if len(ack) > 7:
                    # print(f"Readback: {ack}")
                    if self.isReadBackCorrect(ack):
                        return Status.normal
                if time.time() > time_out:
                    return Status.timeout
            except serial.SerialException as e:
                self.update_com_port()
                print(f"Serial error: {e}")

    def got_Status_respond(self, timeout=3):
        time_out = time.time() + timeout
        while True:
            try:
                ack = self.ser.readline()
                # if len(ack) > 1:
                #     print(f"Readback: {ack}")
                if len(ack) > 7:
                    header, target, action, status, _, _, crc = struct.unpack("=BBBBBBh", ack)
                    # print(f"(got_Status_respond) - {Status(status)}, {status} ")
                    return Status(status)
                if time.time() > time_out:
                    self.update_com_port()
                    # return Status.timeout # FIXME - IDK why its not returning any reading time by time, so just bypass
                    return Status.normal
            except serial.SerialException as e:
                self.update_com_port()
                print(f"Serial error: {e}")

    def phase_sensor_msg(self, timeout=3):
        time_out = time.time() + timeout
        while True:
            try:
                ack = self.ser.readline()
                # if len(ack) > 1:
                #     print(ack)
                if len(ack) > 7:
                    header, target, s3, s2, s1, s0, crc = struct.unpack("=BBBBBBh", ack)
                    return (s0, s1, s2, s3)
                if time.time() > time_out:
                    self.update_com_port()
                    return (0, 0, 0, 0)
            except serial.SerialException as e:
                self.update_com_port()
                print(f"Serial error: {e}")

    def generate_crc16(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF

    # ========================================== Action ========================================== #
    def unloader_init(self):
        if not self.is_com_ready():
            return False
        if not self.is_readback_status_normal(self.unloader_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("02")
        hex_message += bytearray.fromhex("03")
        hex_message += bytearray.fromhex("01")  # PARAM1
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.unloader_status = self.got_Status_respond(timeout=20)
        return True if self.is_readback_status_normal(self.unloader_status) else False

    def starWheel_init(self):
        if not self.is_com_ready():
            return False
        if not self.is_readback_status_normal(self.star_wheel_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("03")
        hex_message += bytearray.fromhex("01")  # PARAM1
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_Status_respond(timeout=65)
        if self.is_readback_status_normal(self.star_wheel_status):
            self.timer.reset()
            return True
        else:
            return False

    def star_wheel_move_back(self, step=1):
        if not self.is_com_ready():
            return False
        if not self.is_readback_status_normal(self.star_wheel_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("FF")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)
        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_ACK_respond()
        return True if self.is_readback_status_normal(self.star_wheel_status) else False

    def star_wheel_move_ms(self, time_ms):
        if not self.is_com_ready():
            return False
        if not self.is_readback_status_normal(self.star_wheel_status):
            return False
        if not self.timer.is_inited():
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("05")
        max(min(5000, time_ms), 600)
        hex_message += struct.pack("<H", time_ms)
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_Status_respond()
        # if self.star_wheel_status == Status.timeout:
        #     self.update_com_port()
        #     self.star_wheel_move_ms(time_ms)
        # print(f"Star Wheel Move ms readback: { self.star_wheel_status}")
        if self.is_readback_status_normal(self.star_wheel_status):
            self.timer.move_index()
            return True
        else:
            return False
        # print("-".join("{:02x}".format(x) for x in hex_message))
        # return hex_message

    def star_wheel_clear_error(self):
        if not self.is_com_ready():
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("06")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_ACK_respond()
        self.star_wheel_status = Status.not_init
        return True if self.is_readback_status_normal(self.star_wheel_status) else False

    def unload(self):
        if not self.is_com_ready():
            return False
        if not self.is_readback_status_normal(self.unloader_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("02")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("01")  # PARAM1
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)
        t1 = time.time()
        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.unloader_status = self.got_Status_respond()
        print("unloader time: ", t1 - time.time())
        if self.is_readback_status_normal(self.unloader_status):
            self.timer.update_slot()
            return True
        else:
            return False

    def unloader_clear_error(self):
        if not self.is_com_ready():
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("02")
        hex_message += bytearray.fromhex("06")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.unloader_status = self.got_ACK_respond()
        return True if self.is_readback_status_normal(self.unloader_status) else False

    # -------------------------------------------------------------------------------------------- #
    def askStarWheelStep(self):
        if not self.is_com_ready():
            return Status.error
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("BB")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("06")  # PARAM1
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        return self.got_ACK_respond()
        # print("-".join("{:02x}".format(x) for x in hex_message))
        # return hex_message

    def ask_sensors(self):
        if not self.is_com_ready():
            return None
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("BB")
        hex_message += bytearray.fromhex("03")
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")  # PARAM1
        hex_message += bytearray.fromhex("00")
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        # print(self.phase_sensor_msg())
        # print("-".join("{:02x}".format(x) for x in hex_message))
        return self.phase_sensor_msg()

    # -------------------------------------------------------------------------------------------- #
    def isReadBackCorrect(self, msg):
        return msg == b"ACK\x00\x00\x00\x00\x00"

    def is_readback_status_normal(self, status):
        return (status is Status.idle) or (status is Status.normal) or (status is Status.not_init)

    # ------------------------------------------------------------------------------------------- #
    def resolve_sensor_status(self, sensor, id: int, low: int = 80, high: int = 100):
        if (id < 0) or (id > 4):  # Input error
            return -3
        if sensor is None:
            return -2
        elif sensor[id] == 0:  # Sensor Error
            return -1
        elif sensor[id] <= low:  # Low
            return 0
        elif sensor[id] >= high:  # High
            return 1
        else:  # Not connected or error
            return -2

    # -------------------------------------------------------------------------------------------- #

    def star_wheel_move_count(self, count):
        if not self.is_readback_status_normal(self.star_wheel_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("07")
        max(min(0, count), 255)
        hex_message += struct.pack("<H", count)
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_Status_respond()
        # print(f"Star Wheel Move ms readback: { self.star_wheel_status}")
        return True if self.is_readback_status_normal(self.star_wheel_status) else False
        # print("-".join("{:02x}".format(x) for x in hex_message))
        # return hex_message

    def starWheel_save_offset(self, count):
        if not self.is_readback_status_normal(self.star_wheel_status):
            return False
        # Hex message to send
        hex_message = []
        hex_message += bytearray.fromhex("AA")
        hex_message += bytearray.fromhex("01")
        hex_message += bytearray.fromhex("08")
        hex_message += struct.pack("<H", count)  # PARAM1
        hex_message += bytearray.fromhex("00")
        crc = self.generate_crc16(hex_message)
        hex_message += struct.pack("<H", crc)

        try:
            self.ser.write(hex_message)
        except serial.SerialException as e:
            self.update_com_port()
            print(f"Serial error: {e}")
        self.star_wheel_status = self.got_Status_respond()
        return True if self.is_readback_status_normal(self.star_wheel_status) else False


if __name__ == "__main__":
    USING_TINKER = False

    try:
        with BScbAPI(port="COM5", baud_rate=115200) as board:
            if board.is_com_ready():
                if not board.star_wheel_clear_error():
                    print(f"Star wheel clear error error, see error {board.star_wheel_status}")
                else:
                    print("Clear star wheel error")

                if not board.unloader_clear_error():
                    print(f"unloader clear error error, see error {board.unloader_status}")
                else:
                    print("Clear unloader error")

                # if not board.starWheel_init():
                #     print(f"Star wheel init error, see error {board.star_wheel_status}")
                # else:
                #     print("Start wheel inited")

                # print("move 1")
                # print(board.star_wheel_move_ms(600))

                board.starWheel_init()
                count = 0
                # print(board.star_wheel_move_count(count))
                # time.sleep(1)
                # print(board.starWheel_save_offset(count))

                # print("move -1")
                # print(board.star_wheel_move_back())

                # if not board.unloader_init():
                #     print(f"Unloader init error, see error {board.unloader_status}")
                # else:
                #     print("Unloader inited")

                # for _ in range(10):
                #     # board.ask_sensors()
                #     # board.star_wheel_move_ms(600)
                #     if not board.star_wheel_move_ms(600):
                #         print(f"Star wheel move error, see error {board.star_wheel_status}")
                #         break
                #     else:
                #         print("OK")
                #     # board.star_wheel_move_ms(3000)
                #     # board.star_wheel_move()
                #     if not board.unload():
                #         print(f"Unloader error, see error {board.unloader_status}")
                #         break
                #     else:
                # print("OK")
            else:
                print("Error - No Controller found")
    except Exception as e:
        print(f"Error: {e}")
