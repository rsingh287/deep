"""
ੴ Sikh Heritage & Gurbani Routes Blueprint
Local AI PC Cockpit - 100% Offline
"""

from flask import Blueprint, request, jsonify, render_template
import sikh_heritage_engine

gurbani_bp = Blueprint("gurbani", __name__)

@gurbani_bp.route("/gurbani")
def gurbani_portal_view():
    """Renders the dedicated offline Sikh Heritage & Gurbani Cockpit portal."""
    try:
        contemplation = sikh_heritage_engine.get_daily_contemplation()
        baanis = list(sikh_heritage_engine.NITNEM_BAANIS.values())
        return render_template("gurbani.html", contemplation=contemplation, baanis=baanis)
    except Exception as e:
        return f"Error loading Gurbani Portal: {e}", 500

@gurbani_bp.route("/api/gurbani/baanis", methods=["GET"])
def api_get_baanis():
    """Returns all daily Nitnem Baanis with local availability indicators."""
    try:
        results = []
        for key, info in sikh_heritage_engine.NITNEM_BAANIS.items():
            local_track = sikh_heritage_engine.find_local_baani_audio(key)
            item = dict(info)
            item["has_local_audio"] = bool(local_track)
            item["local_filename"] = local_track["filename"] if local_track else None
            results.append(item)
        return jsonify({"status": "success", "baanis": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@gurbani_bp.route("/api/gurbani/play", methods=["POST"])
def api_play_gurbani():
    """Plays requested Baani on PC Speakers."""
    try:
        data = request.get_json() or {}
        query = data.get("query") or data.get("baani_id") or "japji_sahib"
        res = sikh_heritage_engine.play_gurbani_audio(query)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@gurbani_bp.route("/api/gurbani/contemplation", methods=["GET"])
def api_get_contemplation():
    """Returns today's contemplation verse."""
    try:
        verse = sikh_heritage_engine.get_daily_contemplation()
        return jsonify({"status": "success", "contemplation": verse})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@gurbani_bp.route("/api/gurbani/search", methods=["POST"])
def api_search_heritage():
    """Searches offline Sikh Heritage knowledge base."""
    try:
        data = request.get_json() or {}
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"status": "error", "message": "Query required"}), 400
        res = sikh_heritage_engine.search_heritage_knowledge(query)
        if res:
            return jsonify({"status": "success", "result": res})
        else:
            return jsonify({"status": "not_found", "message": "No direct match in offline heritage database."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
