"""
tshark -> /api/network-events forwarder

Usage:
  - configure CAPTURE_INTERFACE and ENDPOINT below (or via env vars)
  - run with python3 forwarder.py
"""

import os
import shlex
import subprocess
import threading
import time
import json
from queue import Queue, Empty
from typing import Optional, Dict, Any, List

import requests

# Config (change as needed)
CAPTURE_INTERFACE = os.getenv("CAPTURE_INTERFACE", "\\Device\\NPF_{0C16F9BC-AD3A-4F18-AEAA-55E9A315A4F3}")   # e.g. "eth0" or "any"
ENDPOINT = os.getenv("ENDPOINT", "http://127.0.0.1:3003/api/net/events")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))             # send after this many events
BATCH_INTERVAL = float(os.getenv("BATCH_INTERVAL", "2.0"))  # send at least every N seconds
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
LOG_PREFIX = "[tshark-forwarder]"

# Capture filter: exclude HTTP/HTTPS (tcp 80, tcp 443) and UDP 443 (QUIC)
# You can extend this if you want to exclude other ports/protocols.
CAPTURE_FILTER = "not (tcp port 80 or tcp port 443 or udp port 443)"

# Fields to extract from tshark using -T fields
TSHARK_FIELDS = [
    "frame.time_epoch",     # epoch float time
    "frame.number",
    "_ws.col.Protocol",
    "ip.src",
    "ip.dst",
    "ipv6.src",
    "ipv6.dst",
    "tcp.srcport",
    "tcp.dstport",
    "udp.srcport",
    "udp.dstport",
    "frame.len",
    "_ws.col.Info"
]

# Build tshark command
TSHARK_CMD = [
    "tshark",
    "-i", CAPTURE_INTERFACE,
    "-l",                # line buffered
    "-n",                # don't resolve names
    "-q",                # minimize extra output
    "-f", CAPTURE_FILTER, # capture filter (BPF)
    "-T", "fields",
]

# add -e field for each requested field
for f in TSHARK_FIELDS:
    TSHARK_CMD += ["-e", f]

# Use a separator unlikely to appear in fields
TSHARK_CMD += ["-E", "separator=|", "-E", "occurrence=f"]

def log(*args, **kwargs):
    print(LOG_PREFIX, *args, **kwargs)

def string_to_hex(text: str) -> str:
    """Convert string to space-separated hex format like 'AB CD 01 29 32'"""
    if not text:
        return ""
    try:
        # Convert string to bytes using UTF-8 encoding, then to hex
        hex_bytes = text.encode('utf-8').hex().upper()
        # Insert spaces every 2 characters
        return ' '.join(hex_bytes[i:i+2] for i in range(0, len(hex_bytes), 2))
    except Exception:
        return ""

def start_tshark_process() -> subprocess.Popen:
    """Start tshark subprocess, returning Popen object streaming stdout lines."""
    log("Starting tshark on interface", CAPTURE_INTERFACE, "with filter:", CAPTURE_FILTER)
    # Note: If tshark is not in PATH or requires sudo, run accordingly.
    proc = subprocess.Popen(
        TSHARK_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # line-buffered text
        universal_newlines=True,
    )
    return proc

def parse_line_to_event(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single line from tshark -T fields with '|' separator into an event dict.
    Missing fields will appear as empty strings.
    """
    parts = line.rstrip("\n").split("|")
    # sometimes tshark prints blank lines; ignore them
    if not any(parts):
        return None

    # Map fields to values; if less parts than fields, pad
    vals = parts + [""] * (len(TSHARK_FIELDS) - len(parts))
    data = dict(zip(TSHARK_FIELDS, vals))

    # Try normalize IPs: prefer IPv4 if present, else IPv6
    src = data.get("ip.src") or data.get("ipv6.src") or ""
    dst = data.get("ip.dst") or data.get("ipv6.dst") or ""

    def to_int_or_none(x):
        try:
            return int(x)
        except Exception:
            return None

    event = {
        "timestamp": float(data.get("frame.time_epoch") or 0.0),
        "frame_number": to_int_or_none(data.get("frame.number") or 0),
        "protocol": data.get("_ws.col.Protocol") or "",
        "src": src,
        "dst": dst,
        "src_port": to_int_or_none(data.get("tcp.srcport") or data.get("udp.srcport") or ""),
        "dst_port": to_int_or_none(data.get("tcp.dstport") or data.get("udp.dstport") or ""),
        "length": to_int_or_none(data.get("frame.len") or 0),
        "info": string_to_hex(data.get("_ws.col.Info") or ""),
        "info_raw": data.get("_ws.col.Info") or "",  # Keep original for reference
    }
    return event

class SenderThread(threading.Thread):
    def __init__(self, endpoint: str, queue: "Queue[Dict]"):
        super().__init__(daemon=True)
        self.endpoint = endpoint
        self.queue = queue
        self.stop_requested = False

    def run(self):
        batch: List[Dict[str, Any]] = []
        last_send = time.time()
        while not self.stop_requested:
            try:
                ev = self.queue.get(timeout=0.5)
                batch.append(ev)
            except Empty:
                pass

            now = time.time()
            if (len(batch) >= BATCH_SIZE) or (batch and (now - last_send) >= BATCH_INTERVAL):
                self._send_batch(batch)
                batch.clear()
                last_send = now

        # send remaining events before exit
        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: List[Dict[str, Any]]):
        if not batch:
            return
        payload = {"events": batch, "count": len(batch)}
        tries = 0
        while tries <= MAX_RETRIES:
            try:
                r = requests.post(self.endpoint, json=payload, timeout=REQUEST_TIMEOUT)
                if r.status_code >= 200 and r.status_code < 300:
                    log(f"Sent batch of {len(batch)} events -> {self.endpoint} (status {r.status_code})")
                    return
                else:
                    log(f"Unexpected status {r.status_code}: {r.text}")
            except Exception as e:
                log("Error sending batch:", e)
            tries += 1
            sleep_time = RETRY_DELAY * (2 ** (tries - 1))
            log(f"Retrying in {sleep_time:.1f}s (attempt {tries}/{MAX_RETRIES})")
            time.sleep(sleep_time)
        log("Failed to send batch after retries; dropping batch")

def main():
    q: "Queue[Dict]" = Queue()
    sender = SenderThread(ENDPOINT, q)
    sender.start()

    proc = start_tshark_process()
    if proc.stdout is None:
        log("No stdout from tshark; exiting")
        return

    try:
        # read lines from tshark stdout
        for raw_line in proc.stdout:
            if not raw_line:
                continue
            event = parse_line_to_event(raw_line)
            if event:
                q.put(event)

            # optional: print a short summary to console
            # log("pkt", event["frame_number"], event["src"], "->", event["dst"], event["protocol"])

    except KeyboardInterrupt:
        log("Interrupted by user, shutting down")
    finally:
        try:
            proc.kill()
        except Exception:
            pass
        sender.stop_requested = True
        sender.join(timeout=5)
        log("Exiting")

if __name__ == "__main__":
    main()
