"""
Institutional Public APIs Blueprint (35 High-Fidelity Zero-Cost Public Data Feeds)
Connects all 35 APIs from public_apis.py directly to the Cockpit UI:
- Bank of Canada CAD/USD, US CISA KEV, World Bank, NASA JPL, USGS Earthquakes, GitHub Events, etc.
"""

from flask import Blueprint, request, jsonify
import public_apis

public_bp = Blueprint("public_apis", __name__)

API_MAP = {
    "cad_usd": lambda p: public_apis.get_cad_usd_rate(),
    "cisa_kev": lambda p: public_apis.get_cisa_kev(),
    "world_bank": lambda p: public_apis.get_world_bank_data(p.get("country", "CAN"), p.get("indicator", "NY.GDP.MKTP.CD")),
    "nasa": lambda p: public_apis.get_nasa_asteroids(),
    "earthquakes": lambda p: public_apis.get_recent_earthquakes(),
    "github_events": lambda p: public_apis.get_github_events(),
    "openalex": lambda p: public_apis.search_openalex(p.get("query", "quantum computing")),
    "huggingface": lambda p: public_apis.search_huggingface(p.get("query", "qwen")),
    "nvd_cve": lambda p: public_apis.search_nvd_cve(p.get("query", "injection")),
    "open_library": lambda p: public_apis.search_open_library(p.get("query", "artificial intelligence")),
    "statcan": lambda p: public_apis.get_statcan_data(p.get("productId", "36100104")),
    "sec_edgar": lambda p: public_apis.get_sec_edgar(p.get("cik", "0000320193")),
    "osv": lambda p: public_apis.check_osv_vulnerabilities(p.get("package", "requests"), p.get("version", "2.20.0")),
    "defillama_protocols": lambda p: public_apis.get_defillama_protocols(),
    "defillama_yields": lambda p: public_apis.get_defillama_yields(),
    "overpass": lambda p: public_apis.query_overpass(p.get("query", "node[amenity=hospital](46.4,-81.1,46.6,-80.9);out;")),
    "wikidata": lambda p: public_apis.query_wikidata(p.get("query", "SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q146. SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". } } LIMIT 5")),
    "radio": lambda p: public_apis.search_radio_stations(p.get("name", "chill")),
    "arxiv": lambda p: public_apis.search_arxiv(p.get("query", "machine learning")),
    "wayback": lambda p: public_apis.search_wayback_machine(p.get("url", "https://github.com")),
    "clinical_trials": lambda p: public_apis.get_clinical_trials(p.get("query", "cancer")),
    "openfda": lambda p: public_apis.search_openfda(p.get("query", "aspirin")),
    "openaq": lambda p: public_apis.get_openaq_data(p.get("city", "Toronto")),
    "crossref": lambda p: public_apis.search_crossref(p.get("query", "neural network")),
    "lichess": lambda p: public_apis.get_lichess_user(p.get("username", "magnuscarlsen")),
    "europe_pmc": lambda p: public_apis.search_europe_pmc(p.get("query", "CRISPR")),
    "who_gho": lambda p: public_apis.get_who_gho_data(),
    "open_elevation": lambda p: public_apis.get_open_elevation(p.get("lat", 46.49), p.get("lng", -80.99)),
    "sunrise_sunset": lambda p: public_apis.get_sunrise_sunset(p.get("lat", 46.49), p.get("lng", -80.99)),
    "gutenberg": lambda p: public_apis.search_gutenberg(p.get("query", "frankestein")),
    "nominatim": lambda p: public_apis.query_nominatim(p.get("query", "Sudbury, Ontario")),
    "fred": lambda p: public_apis.get_fred_data(p.get("seriesId", "GDP")),
    "nasa_firms": lambda p: public_apis.get_nasa_firms(),
    "barents_watch": lambda p: public_apis.get_barents_watch(),
    "open_meteo": lambda p: public_apis.get_open_meteo(p.get("lat", 46.49), p.get("lng", -80.99))
}


@public_bp.route("/api/public/list", methods=["GET"])
def list_all_public_apis():
    """Returns the full catalog of all 35 Institutional Public APIs."""
    apis = []
    for k in API_MAP.keys():
        apis.append({
            "id": k,
            "endpoint": f"/api/public/{k}",
            "status": "ONLINE",
            "type": "REST_JSON"
        })
    return jsonify({
        "status": "success",
        "total_apis": len(apis),
        "catalog": apis
    })


@public_bp.route("/api/public/<api_name>", methods=["GET", "POST"])
def call_public_api(api_name: str):
    """Executes any of the 35 Institutional Public APIs by name."""
    handler = API_MAP.get(api_name.lower())
    if not handler:
        return jsonify({
            "status": "error",
            "error": f"API '{api_name}' not found. Available APIs: {list(API_MAP.keys())}"
        }), 404

    params = {}
    if request.method == "POST":
        params = request.get_json(force=True, silent=True) or {}
    else:
        params = request.args.to_dict()

    try:
        result = handler(params)
        return jsonify({
            "status": "success",
            "api": api_name,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "api": api_name,
            "error": str(e)
        }), 500
