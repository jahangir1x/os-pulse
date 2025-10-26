# forward_events.py
from mitmproxy import http
from mitmproxy.tools.main import mitmdump
import requests
import json
import base64
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logger = logging.getLogger(__name__)

# Configure this to your API endpoint (full URL)
API_URL = "http://127.0.0.1:3003/network-monitor/http/events"

# Max bytes of body to include before truncating (adjust as needed)
MAX_BODY_BYTES = 100 * 1024  # 100 KB

# Thread pool for non-blocking HTTP posts
executor = ThreadPoolExecutor(max_workers=4)

def _safe_b64(data: bytes):
    return base64.b64encode(data).decode("ascii")

def _prepare_body(content: bytes):
    if content is None:
        return None
    size = len(content)
    truncated = False
    if size > MAX_BODY_BYTES:
        content = content[:MAX_BODY_BYTES]
        truncated = True
    try:
        # try decode as utf-8
        text = content.decode("utf-8")
        return {"type": "text", "content": text, "size": size, "truncated": truncated}
    except Exception:
        # binary -> base64
        return {"type": "binary", "content_b64": _safe_b64(content), "size": size, "truncated": truncated}

def _flow_to_event(flow: http.HTTPFlow, kind: str):
    """kind is 'request' or 'response' depending on what triggered this."""
    ts = int(time.time() * 1000)
    try:
        client_addr = None
        if flow.client_conn:
            client_addr = {
                "ip": flow.client_conn.ip_address[0] if flow.client_conn.ip_address else None,
                "port": flow.client_conn.ip_address[1] if flow.client_conn.ip_address else None
            }
    except Exception:
        client_addr = None

    try:
        server_addr = None
        if flow.server_conn:
            server_addr = {
                "ip": getattr(flow.server_conn, "address", None),
            }
    except Exception:
        server_addr = None

    req = flow.request
    evt = {
        "timestamp_ms": ts,
        "kind": kind,
        "client": client_addr,
        "server": server_addr,
        "request": {
            "method": req.method,
            "scheme": req.scheme,
            "host": req.host,
            "port": req.port,
            "path": req.path,
            "url": req.pretty_url,
            "http_version": req.http_version,
            "headers": dict(req.headers),
            "body": _prepare_body(req.raw_content) if req.raw_content is not None else None,
        },
    }

    # Add response info if available
    if flow.response:
        res = flow.response
        evt["response"] = {
            "status_code": res.status_code,
            "reason": res.reason,
            "http_version": res.http_version,
            "headers": dict(res.headers),
            "body": _prepare_body(res.raw_content) if res.raw_content is not None else None,
        }

    # timings (if available)
    try:
        if hasattr(flow, "timestamps") and flow.timestamps:
            evt["timings"] = {k: v for k, v in flow.timestamps.items() if v is not None}
    except Exception:
        pass

    return evt

def _post_event(payload):
    """Send JSON payload to API_URL. Non-blocking wrapper invoked via executor."""
    headers = {"Content-Type": "application/json"}
    try:
        # NOTE: if mitmproxy is set system-wide as an HTTP proxy this request
        # might also be proxied. See run instructions below about NO_PROXY / trust_env.
        r = requests.post(API_URL, json=payload, headers=headers, timeout=3)
        logger.debug(f"forward_events: posted {payload.get('kind')} -> {r.status_code}")
    except Exception as e:
        logger.warning(f"forward_events: failed to POST event: {e}")

class Forwarder:
    def __init__(self):
        logger.info("forward_events addon loaded. Forwarding to: %s" % API_URL)

    def request(self, flow: http.HTTPFlow):
        # Called when a client request has been received
        try:
            payload = _flow_to_event(flow, "request")
            # Don't block the proxy: submit to executor
            executor.submit(_post_event, payload)
        except Exception as e:
            logger.warning(f"forward_events.request error: {e}")

    def response(self, flow: http.HTTPFlow):
        # Called when a response has been received from the server
        try:
            payload = _flow_to_event(flow, "response")
            executor.submit(_post_event, payload)
        except Exception as e:
            logger.warning(f"forward_events.response error: {e}")

addons = [
    Forwarder()
]
