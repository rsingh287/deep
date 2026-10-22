import requests

try:
    response = requests.get("http://localhost:8000/health")
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(e)
