from __future__ import annotations
from dataclasses import dataclass
import psutil
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class NetworkRecord:

    device_name: str
    timestamp: float
    adapter: str
    down_mbps: float
    up_mbps: float
    rx_bytes: int
    tx_bytes: int
