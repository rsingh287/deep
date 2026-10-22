import os
import base64
import pypdf
from flask import Blueprint, request, jsonify

ingestion_bp = Blueprint("ingestion_bp", __name__)

@ingestion_bp.route("/api/upload_context", methods=["POST"])
def upload_context():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    
    try:
        # Images: return Base64
        if ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
            data = file.read()
            b64 = base64.b64encode(data).decode("utf-8")
            return jsonify({
                "type": "image",
                "filename": file.filename,
                "base64": b64
            })
            
        # PDF: return text
        elif ext == "pdf":
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return jsonify({
                "type": "text",
                "filename": file.filename,
                "content": text.strip()
            })
            
        # CSV/TXT/MD: return text
        elif ext in ["csv", "txt", "md", "json", "py", "js", "html", "css", "log"]:
            content = file.read().decode("utf-8")
            return jsonify({
                "type": "text",
                "filename": file.filename,
                "content": content
            })
            
        else:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
