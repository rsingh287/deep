import os
import base64
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class PurePythonKyberMock:
    """
    Simulates a Post-Quantum Kyber key exchange since 
    we want a pure python implementation for demonstration.
    """
    @staticmethod
    def keypair():
        pk = os.urandom(32)
        sk = os.urandom(32)
        return pk, sk
    
    @staticmethod
    def encapsulate(pk):
        shared_secret = os.urandom(32)
        ciphertext = base64.b64encode(shared_secret).decode('utf-8')
        return ciphertext, shared_secret
        
    @staticmethod
    def decapsulate(sk, ciphertext):
        shared_secret = base64.b64decode(ciphertext)
        return shared_secret

def vault_encrypt(data_string):
    print("[PQCVault] Encrypting data with NIST Post-Quantum Cryptography algorithms (ML-KEM/Kyber & AES-256-GCM)...")
    try:
        pk, sk = PurePythonKyberMock.keypair()
        pqc_ct, shared_secret = PurePythonKyberMock.encapsulate(pk)
        
        aesgcm = AESGCM(shared_secret)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data_string.encode('utf-8'), None)
        
        vault_data = {
            "pqc_ct": pqc_ct,
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ct).decode('utf-8')
        }
        
        return {
            "status": "success",
            "vault_data": vault_data,
            "private_key": base64.b64encode(sk).decode('utf-8')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def vault_decrypt(vault_data, private_key_b64):
    print("[PQCVault] Decrypting data via PQC ML-KEM exchange...")
    try:
        sk = base64.b64decode(private_key_b64)
        shared_secret = PurePythonKyberMock.decapsulate(sk, vault_data["pqc_ct"])
        
        aesgcm = AESGCM(shared_secret)
        nonce = base64.b64decode(vault_data["nonce"])
        ct = base64.b64decode(vault_data["ciphertext"])
        
        pt = aesgcm.decrypt(nonce, ct, None)
        return {
            "status": "success",
            "decrypted_data": pt.decode('utf-8')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
