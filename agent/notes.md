/api/events/events
{
  "event_type": "file_operation",
  "timestamp": "2025-10-27T07:06:20.870008Z",
  "source": "os-pulse-controller",
  "data": {
    "handle": "0x1348",
    "filePath": "\\\\?\\C:\\Users\\rocky\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\f01b4d95cf55d32a.automaticDestinations-ms",
    "bytesTransferred": 4,
    "content": "72 00 00 00",
    "timestamp": "2025-10-27T07:05:55.624Z",
    "operation": "ReadFile",
    "metadata": {
      "sessionId": "mh8sn69b-8408128070982301",
      "processName": "Notepad.exe",
      "processId": 9144
    }
  }
}

/api/events/events
{
  "event_type": "file_operation",
  "timestamp": "2025-10-27T07:11:18.096907Z",
  "source": "os-pulse-controller",
  "data": {
    "handle": "0x1810",
    "filePath": "\\\\?\\C:\\Users\\rocky\\Desktop\\asfdasd sdfasdfasd.txt",
    "bytesTransferred": 18,
    "content": "61 73 66 64 61 73 64 20 73 64 66 61 73 64 66 61 73 64",
    "timestamp": "2025-10-27T07:11:12.552Z",
    "operation": "WriteFile",
    "metadata": {
      "sessionId": "mh8stp2g-7568185157154355",
      "processName": "Notepad.exe",
      "processId": 9144
    }
  }
}

/api/http/events
{
  "timestamp_ms": 1761549204774,
  "kind": "response",
  "client": null,
  "server": {
    "ip": [
      "safebrowsing.googleapis.com",
      443
    ]
  },
  "request": {
    "method": "GET",
    "scheme": "https",
    "host": "safebrowsing.googleapis.com",
    "port": 443,
    "path": "/v4/threatListUpdates:fetch?$ct=application/x-protobuf&key=AIzaSyC7jsptDS3am4tPx4r3nxis7IMjBc5Dovo&$httpMethod=POST&$req=ChUKE25hdmNsaWVudC1hdXRvLWZmb3gaJwgFEAEaGwoNCAUQBhgBIgMwMDEwARCBsx0aAhgDbwi89CICIAIoARonCAEQARobCg0IARAGGAEiAzAwMTABEPnZEhoCGAN_cXHhIgIgAigBGicIAxABGhsKDQgDEAYYASIDMDAxMAEQldISGgIYA7j_32YiAiACKAEaJwgHEAEaGwoNCAcQBhgBIgMwMDEwARCy7xIaAhgDCpVITCICIAIoARolCAkQARoZCg0ICRAGGAEiAzAwMTABECMaAhgD4HOyDyICIAIoAQ==",
    "url": "https://safebrowsing.googleapis.com/v4/threatListUpdates:fetch?$ct=application/x-protobuf&key=AIzaSyC7jsptDS3am4tPx4r3nxis7IMjBc5Dovo&$httpMethod=POST&$req=ChUKE25hdmNsaWVudC1hdXRvLWZmb3gaJwgFEAEaGwoNCAUQBhgBIgMwMDEwARCBsx0aAhgDbwi89CICIAIoARonCAEQARobCg0IARAGGAEiAzAwMTABEPnZEhoCGAN_cXHhIgIgAigBGicIAxABGhsKDQgDEAYYASIDMDAxMAEQldISGgIYA7j_32YiAiACKAEaJwgHEAEaGwoNCAcQBhgBIgMwMDEwARCy7xIaAhgDCpVITCICIAIoARolCAkQARoZCg0ICRAGGAEiAzAwMTABECMaAhgD4HOyDyICIAIoAQ==",
    "http_version": "HTTP/2.0",
    "headers": {
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
      "accept": "*/*",
      "accept-language": "en-US,en;q=0.5",
      "accept-encoding": "gzip, deflate, br, zstd",
      "x-http-method-override": "POST",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "no-cors",
      "sec-fetch-site": "none",
      "priority": "u=4",
      "pragma": "no-cache",
      "cache-control": "no-cache",
      "te": "trailers"
    },
    "body": {
      "type": "text",
      "content": "",
      "size": 0,
      "truncated": false
    }
  },
  "response": {
    "status_code": 200,
    "reason": "",
    "http_version": "HTTP/2.0",
    "headers": {
      "vary": "Accept-Encoding",
      "content-type": "application/x-protobuf",
      "content-disposition": "attachment",
      "date": "Mon, 27 Oct 2025 07:13:24 GMT",
      "server": "scaffolding on HTTPServer2",
      "content-length": "52570",
      "x-xss-protection": "0",
      "x-frame-options": "SAMEORIGIN",
      "x-content-type-options": "nosniff",
      "alt-svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
    },
    "body": {
      "type": "binary",
      "content_b64": "CtjhAggFEAEYASABKpetAQgCIpGtAQjE9hUQEhjeQyKErQErRvekXxEUa+zrEIX6t6HyTb+sIpL4gkCcIZy4dQOrkc9Oe53rpGl68FRleiDdDZKL1KjxSpAj+e7nG0Js/VtgB+dc5/npwHG8SdBRWBiunzvXGrJFlCLadYj/uyJ/2yXcnWqVdz+m/PbG5Yj1obWz473G+oUJddyWu6ogt==",
      "size": 52570,
      "truncated": false
    }
  }
}

/api/net/events
{
  "events": [
    {
      "timestamp": 1761550168.708248,
      "frame_number": 1,
      "protocol": "ARP",
      "src": "",
      "dst": "",
      "src_port": null,
      "dst_port": null,
      "length": 60,
      "info": "57 68 6F 20 68 61 73 20 31 30 2E 31 31 30 2E 34 38 2E 31 3F 20 54 65 6C 6C 20 31 30 2E 31 31 30 2E 35 30 2E 31 32 39",
      "info_raw": "Who has 10.110.48.1? Tell 10.110.50.129"
    },
    {
      "timestamp": 1761550168.710248,
      "frame_number": 2,
      "protocol": "ARP",
      "src": "",
      "dst": "",
      "src_port": null,
      "dst_port": null,
      "length": 60,
      "info": "57 68 6F 20 68 61 73 20 31 30 2E 31 31 30 2E 34 38 2E 31 3F 20 54 65 6C 6C 20 31 30 2E 31 31 30 2E 35 30 2E 31 32 39",
      "info_raw": "Who has 10.110.48.1? Tell 10.110.50.129"
    },
    ...
  ]
}

