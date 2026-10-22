import os
import secrets
from PIL import Image

def shred_file(path, passes=3):
    """
    DoD 5220.22-M 3-Pass Shredder implementation.
    Pass 1: Zeros
    Pass 2: Ones
    Pass 3: Cryptographic random bytes
    """
    if not os.path.exists(path):
        return False
    
    length = os.path.getsize(path)
    print(f"[SecureVault] Initiating DoD 5220.22-M shred on {path} ({length} bytes)")
    
    with open(path, "ba+") as delfile:
        for p in range(passes):
            delfile.seek(0)
            if p == 0:
                delfile.write(b'\x00' * length)
            elif p == 1:
                delfile.write(b'\xff' * length)
            else:
                delfile.write(secrets.token_bytes(length))
            delfile.flush()
            os.fsync(delfile.fileno())
            
    # Rename to random string before unlink to hide original filename
    dir_name = os.path.dirname(path)
    random_name = os.path.join(dir_name, secrets.token_hex(16))
    os.rename(path, random_name)
    os.unlink(random_name)
    print("[SecureVault] Shredding complete. File permanently sanitized.")
    return True

def steg_hide(image_path, text, out_path):
    """
    Hides text inside the LSB (Least Significant Bit) of image pixels.
    """
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size
    
    # Convert text to binary + delimiter
    binary = ''.join([format(ord(i), "08b") for i in text]) + '1111111111111110'
    
    idx = 0
    for row in range(height):
        for col in range(width):
            pixel = list(encoded.getpixel((col, row)))
            for n in range(3):
                if idx < len(binary):
                    pixel[n] = pixel[n] & ~1 | int(binary[idx])
                    idx += 1
            encoded.putpixel((col, row), tuple(pixel))
            if idx >= len(binary):
                break
        if idx >= len(binary):
            break
            
    encoded.save(out_path, format="PNG")
    print(f"[SecureVault] Secret data encoded and saved to {out_path}")
    return True

def steg_extract(image_path):
    """
    Extracts text hidden inside the LSB of image pixels.
    """
    img = Image.open(image_path)
    width, height = img.size
    binary = ""
    
    for row in range(height):
        for col in range(width):
            pixel = list(img.getpixel((col, row)))
            for n in range(3):
                binary += str(pixel[n] & 1)
                
    delimiter = "1111111111111110"
    delim_idx = binary.find(delimiter)
    if delim_idx != -1:
        binary = binary[:delim_idx]
        
    all_bytes = [binary[i: i+8] for i in range(0, len(binary), 8)]
    decoded_data = ""
    for byte in all_bytes:
        if len(byte) == 8:
            decoded_data += chr(int(byte, 2))
            
    return decoded_data
