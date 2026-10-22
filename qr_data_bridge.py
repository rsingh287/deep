import os

def create_qr_video_bus(data_string, output_path="static/qr_bus.gif", chunk_size=100, fps=10):
    print("[QRDataBridge] Initializing High-Speed Air-Gapped Optical Data Bridge...")
    try:
        import qrcode
        import imageio
        
        chunks = [data_string[i:i+chunk_size] for i in range(0, len(data_string), chunk_size)]
        total = len(chunks)
        frames = []
        
        for i, chunk in enumerate(chunks):
            payload = f"{i+1}/{total}|{chunk}"
            img = qrcode.make(payload)
            img = img.convert("RGB")
            frames.append(img)
            
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        imageio.mimsave(output_path, frames, duration=1000/fps)
        print(f"[QRDataBridge] QR Video Bus created successfully at {output_path}")
        
        return {
            "status": "success",
            "frames": total,
            "output_path": output_path
        }
    except ImportError:
        print("[QRDataBridge] 'qrcode' or 'imageio' not installed. Simulation fallback.")
        return {
            "status": "error",
            "message": "Required libraries (qrcode, imageio) not installed."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
