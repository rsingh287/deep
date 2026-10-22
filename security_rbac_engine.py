"""
Security RBAC Engine & Zero-Trust Gatekeeper
Role-Based Access Control, Secret Detection, PQC-Backed Data Encryption,
and AST Verification for AI Agent Tools and Knowledge Graphs.
"""

import os
import re
import base64
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pqc_vault import vault_encrypt, vault_decrypt
from enterprise_ai_guardrails import enterprise_guardrails

# Role Hierarchies
ROLES = {
    "ADMIN": {
        "level": 4,
        "permissions": {
            "filesystem:read",
            "filesystem:read_lines",
            "filesystem:append",
            "filesystem:delete_quarantine",
            "filesystem:delete_permanent",
            "filesystem:archive",
            "filesystem:symlink",
            "memory:read",
            "memory:write",
            "memory:update",
            "memory:delete",
            "memory:decrypt_sensitive",
            "system:execute_raw",
            "sandbox:execute"
        }
    },
    "DEVELOPER": {
        "level": 3,
        "permissions": {
            "filesystem:read",
            "filesystem:read_lines",
            "filesystem:append",
            "filesystem:delete_quarantine",
            "filesystem:archive",
            "filesystem:symlink",
            "memory:read",
            "memory:write",
            "memory:update",
            "memory:delete",
            "sandbox:execute"
        }
    },
    "OPERATOR": {
        "level": 2,
        "permissions": {
            "filesystem:read",
            "filesystem:read_lines",
            "filesystem:append",
            "memory:read",
            "memory:write",
            "memory:update"
        }
    },
    "READ_ONLY": {
        "level": 1,
        "permissions": {
            "filesystem:read",
            "filesystem:read_lines",
            "memory:read"
        }
    }
}

# Regex heuristics for detecting sensitive credentials & secrets in text
SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token|auth_token|access_token|private_key)(?:[\s:=]+|[\s]+is[\s]+)['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)postgresql://[^:]+:([^@]+)@"),
]


class SecurityRBACEngine:
    def __init__(self, master_key: Optional[bytes] = None):
        # 256-bit AES Master Key for fast local observation encryption
        if master_key and len(master_key) == 32:
            self._master_key = master_key
        else:
            seed = os.getenv("DEEP_SECURITY_MASTER_KEY", "deep_os_master_security_salt_2026_antigravity")
            self._master_key = hashlib.sha256(seed.encode("utf-8")).digest()
        self.aesgcm = AESGCM(self._master_key)

    def verify_permission(self, role: str, required_permission: str) -> Tuple[bool, str]:
        """Validates if a given role possesses the required permission."""
        role_upper = role.upper()
        if role_upper not in ROLES:
            return False, f"Unknown role '{role}'. Permitted roles: {list(ROLES.keys())}"

        granted_permissions = ROLES[role_upper]["permissions"]
        if required_permission not in granted_permissions:
            return False, f"Access Denied: Role '{role_upper}' lacks required permission '{required_permission}'."

        return True, "Authorized"

    def detect_secrets(self, text: str) -> bool:
        """Returns True if the text contains credentials, private keys, or passwords."""
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def redact_secrets(self, text: str) -> str:
        """Masks detected secrets for safe display in logs and telemetry."""
        sanitized = text
        for pattern in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(r"\1: [REDACTED_CREDENTIAL]", sanitized)
        return sanitized

    def encrypt_sensitive_observation(self, observation_text: str, use_pqc: bool = False) -> Dict[str, Any]:
        """
        Encrypts an observation string.
        Supports standard AES-256-GCM or NIST Post-Quantum Kyber Mock via pqc_vault.
        """
        if use_pqc:
            res = vault_encrypt(observation_text)
            if res.get("status") == "success":
                return {
                    "encrypted": True,
                    "method": "PQC_KYBER_AES256",
                    "payload": res["vault_data"],
                    "privKey": res["private_key"]
                }

        # Fast AES-256-GCM
        nonce = os.urandom(12)
        ct = self.aesgcm.encrypt(nonce, observation_text.encode("utf-8"), None)
        return {
            "encrypted": True,
            "method": "AES256_GCM",
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext": base64.b64encode(ct).decode("utf-8")
        }

    def decrypt_sensitive_observation(self, encrypted_record: Dict[str, Any], user_role: str = "ADMIN") -> Dict[str, Any]:
        """
        Decrypts an observation if the caller is authorized.
        """
        allowed, reason = self.verify_permission(user_role, "memory:decrypt_sensitive")
        if not allowed:
            return {"success": False, "error": reason}

        method = encrypted_record.get("method")
        try:
            if method == "PQC_KYBER_AES256":
                vault_data = encrypted_record.get("payload")
                priv_key = encrypted_record.get("privKey")
                res = vault_decrypt(vault_data, priv_key)
                if res.get("status") == "success":
                    return {"success": True, "text": res["decrypted_data"]}
                return {"success": False, "error": res.get("message")}

            elif method == "AES256_GCM":
                nonce = base64.b64decode(encrypted_record["nonce"])
                ct = base64.b64decode(encrypted_record["ciphertext"])
                pt = self.aesgcm.decrypt(nonce, ct, None)
                return {"success": True, "text": pt.decode("utf-8")}
            else:
                return {"success": False, "error": f"Unsupported encryption method: {method}"}
        except Exception as e:
            return {"success": False, "error": f"Decryption failure: {str(e)}"}

    def audit_ast_action(self, action_type: str, payload: str) -> Dict[str, Any]:
        """Verifies actions against enterprise AI AST guardrails."""
        if action_type.lower() == "sql":
            return enterprise_guardrails.validate_text_to_sql(payload)
        return enterprise_guardrails.arbitrate_output(action_type, payload)


# Singleton instance
security_rbac = SecurityRBACEngine()
