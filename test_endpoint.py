import requests
import json

url = "https://mda-horizon-backend-2025.azurewebsites.net/query"
data = {"query_text": "What is Horizon Europe?"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 