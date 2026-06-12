import urllib.request
import urllib.parse
import os
import json
import base64

# Config
CLIENT_ID = "f7955861-3ef1-4dd9-8204-603ec0c7ecb2"
CLIENT_SECRET = "272792c7-d5eb-4fdc-8fbd-fdc316b88c70"
AIP_MANAGEMENT_URL = "https://aiplatform-hcm.api.vngcloud.vn"
IAM_TOKEN_URL = "https://iam.api.vngcloud.vn/accounts-api/v2/auth/token"
KEY_NAME = "my-chatbot-key"

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

def create_api_key(token):
    url = f"{AIP_MANAGEMENT_URL}/v2/api-keys"
    payload = json.dumps({"name": KEY_NAME, "isDefault": False}).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode())
        return res_data

def save_to_env(key):
    env_file = ".env"
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    
    found = False
    new_lines = []
    for line in lines:
        if line.startswith("LLM_API_KEY="):
            new_lines.append(f"LLM_API_KEY={key}\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(f"LLM_API_KEY={key}\n")
    
    with open(env_file, "w") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    try:
        print("Fetching token...")
        token = get_token()
        print("Creating API key...")
        resp = create_api_key(token)
        key_value = resp.get("data", {}).get("key") or resp.get("key")
        if key_value:
            save_to_env(key_value)
            print(f"Successfully created and saved API key for {KEY_NAME}")
        else:
            print(f"API key created but value not found in response: {resp}")
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
