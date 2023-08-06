import socket
import time

from subprocess import call, TimeoutExpired
from pathlib import Path


class Solver:
    def __init__(self, address: str, port: int) -> None:
        self._address = address
        self._port = port
        self._conn: socket = None

        self._debug: bool = False
        self._connected = False

    def connect(self):
        if self._connected:
            return

        # configuration
        matlab_scripts = Path(__file__).parent / "matlab"

        # Start Matlab
        try:
            call(
                f"/usr/local/MATLAB/R2022b/bin/matlab -nosplash -nodesktop -r \"cd('{str(matlab_scripts.absolute())}'); BackgroundSolver("
                + str(self._port)
                + ');exit"',
                shell=True,
                timeout=10,
            )
        except TimeoutExpired:
            # The matlab server does not return, this exception is intended
            pass

        # Connect to server
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.conn.connect((self._address, self._port))
                break
            except:
                time.sleep(1)

        self._connected = True
        return [self.conn, self.conn]

    def disconnect(self):
        if not self._connected:
            return

        self.conn.sendall("end@".encode())
        self._connected = False
        call("stty sane", shell=True)

    def set_timeout(self, timeout: int):
        self.conn.sendall(("timeout;" + str(timeout) + "@").encode())

    def send_command(self, cmd: str):
        self.conn.sendall((cmd + "@").encode())
        ret_val = self.conn.recv(2048).decode()
        return ret_val
