"""
Dynamic API Client Tool: v4_test_fx_client
Description: Dynamic Forex rate fetcher tool
Endpoint: https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json [GET]
"""
import urllib.request
import urllib.parse
import json
from typing import Any, Dict

def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute dynamic HTTP call with zero-trust validation."""
    if not isinstance(args, dict):
        return {"success": False, "error": "Arguments must be a dictionary"}
    
    url = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
    method = "GET"
    query_params = {}
    for k, v in args.items():
        if v is not None:
            query_params[k] = str(v)
            
    if method == "GET" and query_params:
        url = url + "?" + urllib.parse.urlencode(query_params)
        
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DEEP-Sovereign-Agent/4.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = response.read().decode("utf-8")
            try:
                data = json.loads(payload)
            except Exception:
                data = payload
            return {"success": True, "status_code": response.status, "data": data, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}
