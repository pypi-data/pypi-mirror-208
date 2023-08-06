
import os
import sys
import time
import serial
import subprocess
from utils import log


class CnexSerial(object):

    TERA_TERM_PATH = r"C:\Program Files (x86)\teraterm\ttermpro.exe"

    def __init__(self, port, baud_rate=115200, timeout=5):
        self.serial_port = port.upper()
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.default_pattern = b"UART>"

    def close_ttermpro(self):
        cmd = 'wmic process where "Name like \'%ttermpro.exe%\'" get CommandLine,ProcessId'
        output = subprocess.check_output(cmd, shell=True).decode()
        lines = output.strip().split('\n')[1:]
        com_arg = '/C=' + self.serial_port.replace('COM', '')
        for line in lines:
            line = line.strip()
            pid = line.split()[-1]
            if '/C=' not in line:
                log.INFO(f'Killing ttermpro.exe process with PID={pid}')
                subprocess.run(['taskkill', '/F', '/PID', pid])
            elif com_arg in line:
                log.INFO(f'Killing ttermpro.exe process with PID={pid} and {com_arg}')
                subprocess.run(['taskkill', '/F', '/PID', pid])

    def get_serial_number(self):
        return self.serial_port.replace("COM", "")

    def create_log_name(self):
        log_path = os.path.join(os.getcwd(), "log", "UART_LOG")
        if os.path.exists(log_path) is False:
            os.makedirs(log_path)
        time_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        log_name = "_".join(["UART", self.serial_port, time_str, ".log"])
        log_name = os.path.join(log_path, log_name)
        return log_name

    def open_ttermpro(self):
        ini_path = os.path.join(os.path.split(self.TERA_TERM_PATH)[0], "TERATERM.INI")
        print(ini_path)
        serial_number = self.get_serial_number()
        log_name = self.create_log_name()
        log.INFO("Reopen TeraTerm")
        cmd_line = 'start "" "%s" /C=%s /BAUD=%s /F="%s" /L=%s' % (
            self.TERA_TERM_PATH, serial_number, self.baud_rate, ini_path, log_name
        )
        log.INFO(cmd_line)
        os.system(cmd_line)

    def clearspi1(self):
        self.send_command(b"clearspi 1", b"clearspi complete")

    def set_timeout(self, timeout):
        self.ser.timeout = timeout

    def send_command(self, cmd_line, wait_pattern=None):
        self.ser = serial.Serial(port=self.serial_port, baudrate=self.baud_rate, timeout=self.timeout)

        wait_pattern = self.default_pattern if wait_pattern is not None else wait_pattern
        if not self.ser.is_open:
            self.ser.open()
        self.ser.flushInput()
        self.ser.write(b"\n")
        log.INFO(self.ser.read_until(self.default_pattern).decode("ascii"))
        for ch in cmd_line:
            self.ser.write(bytes([ch]))
            sys.stdout.write(self.ser.read_until(bytes([ch])).decode("ascii"))
        self.ser.write(b"\n")
        response = self.ser.read_until(wait_pattern)
        try:
            log.INFO(response.decode("ascii"))
        except Exception as e:
            log.ERR(e)
        self.ser.close()
        return response
