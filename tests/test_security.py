import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "http://localhost:42617/webhook"
headers = {
    "Content-Type": "application/json",
    "X-Webhook-Secret": os.getenv("ZEROCLAW_SECRET", "")
}
payload = {"message": "Ciao Jarvis, come stai?"}


try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
