import re
import hashlib

def generate_alias(secret, prefix):
    # Deterministic cryptographic alias
    hash_val = hashlib.sha256(secret.encode()).hexdigest()[:8].upper()
    return f"{prefix}_{hash_val}"

def mask_code_secrets(code_string):
    print("[ZK-Mask] Scanning and structurally masking sensitive identifiers...")
    
    masked_code = code_string
    
    # Simple regex to catch IPs
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ips = set(re.findall(ip_pattern, masked_code))
    for ip in ips:
        if ip != "127.0.0.1" and ip != "0.0.0.0":
            masked_code = masked_code.replace(ip, generate_alias(ip, "SECURE_IP"))
        
    # Simple regex to catch URLs (postgres://, mysql://, etc)
    url_pattern = r'(postgres|mysql|mongodb)://[^ \n\"\']+'
    urls = set(re.findall(url_pattern, masked_code))
    for url_match in urls:
        masked_code = masked_code.replace(url_match, "psql://SECURE_NODE_ALPHA:PORT")
        
    # Tokens/Passwords (e.g. Bearer xyz, password="xyz")
    token_pattern = r'(Bearer |password=|token=|api_key=)([\w\d\-]{10,})'
    def token_repl(m):
        return m.group(1) + generate_alias(m.group(2), "SECURE_TOKEN")
    
    masked_code = re.sub(token_pattern, token_repl, masked_code)
    
    return {
        "status": "success",
        "masked_code": masked_code,
        "message": "Zero-Knowledge structural masking complete."
    }
