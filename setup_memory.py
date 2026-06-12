import urllib.request
import urllib.parse
import os
import json
import base64

# Config
CLIENT_ID = "f7955861-3ef1-4dd9-8204-603ec0c7ecb2"
CLIENT_SECRET = "272792c7-d5eb-4fdc-8fbd-fdc316b88c70"
MEMORY_URL = "https://agentbase.api.vngcloud.vn/memory/memories"
IAM_TOKEN_URL = "https://iam.api.vngcloud.vn/accounts-api/v2/auth/token"
MEMORY_NAME = "my-chatbot-memory"

def get_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    req = urllib.request.Request(IAM_TOKEN_URL, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode())
        return res_data.get("access_token")

def create_memory(token):
    payload = {
        "name": MEMORY_NAME,
        "description": "Bộ nhớ cho chatbot tư vấn hộ kinh doanh của anh Tuấn",
        "eventExpiryDuration": 30,
        "longTermMemoryStrategies": [
            {
                "name": "default-semantic",
                "type": "SEMANTIC",
                "namespaceTemplate": "/strategies/{memoryStrategyId}/actors/{actorId}",
                "enableAutomaticMemoryRecordGeneration": True
            }
        ]
    }
    encoded_payload = json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(MEMORY_URL, data=encoded_payload, headers=headers)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode())
        return res_data

def save_to_env(key, value):
    env_file = ".env"
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(f"{key}={value}\n")
    
    with open(env_file, "w") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    try:
        print("Fetching token...")
        token = get_token()
        print("Creating memory store...")
        resp = create_memory(token)
        memory_id = resp.get("id") or resp.get("data", {}).get("id")
        if memory_id:
            save_to_env("MEMORY_ID", memory_id)
            print(f"Successfully created memory store. ID: {memory_id}")
        else:
            print(f"Memory created but ID not found in response: {resp}")
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
