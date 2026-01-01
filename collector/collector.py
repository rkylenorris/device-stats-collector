from __future__ import annotations

import time
from pathlib import Path
from dotenv import load_dotenv
import os
import socket

import psutil

load_dotenv()

network_adapter = os.getenv("NETWORK_ADAPTER", "Ethernet")


class Collector:

    def __init__(self) -> None:
        self.device_name = socket.gethostname().strip()
        self.network_adapter = os.getenv("NETWORK_ADAPTER", "Wi-Fi")
        self.network = ''
        self.ram = ''
        self.vram = ''
        self.cpu = ''
        self.disk = ''
