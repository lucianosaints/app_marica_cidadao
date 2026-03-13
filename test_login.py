import requests
import json

url = "http://127.0.0.1:8000/api/login/"
payload = {"username": "teste", "password": "teste_password"}
headers = {"Content-Type": "application/json"}

try:
    print(f"Testando conexão com {url}...")
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro ao conectar: {e}")
