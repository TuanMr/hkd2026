import urllib.request
import json
import base64

CLIENT_ID = "f7955861-3ef1-4dd9-8204-603ec0c7ecb2"
CLIENT_SECRET = "272792c7-d5eb-4fdc-8fbd-fdc316b88c70"
IAM_TOKEN_URL = "https://iam.api.vngcloud.vn/accounts-api/v2/auth/token"
FLAVORS_URL = "https://agentbase.api.vngcloud.vn/runtime/flavors"

def get_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    data = "grant_type=client_credentials".encode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    req = urllib.request.Request(IAM_TOKEN_URL, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode()).get("access_token")

def get_flavors(token):
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(FLAVORS_URL, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

if __name__ == "__main__":
    try:
        token = get_token()
        flavors = get_flavors(token)
        # The API response typically has a 'listData' field for lists
        data = flavors.get('listData', flavors) if isinstance(flavors, dict) else flavors
        
        runtime_flavors = [f for f in data if 'agent-runtime' in f.get('supportedResourceTypes', [])]
        for f in runtime_flavors:
            print(f"ID: {f['id']} | CPU: {f['cpu']} | RAM: {f['ram']} | Name: {f.get('name', 'N/A')}")
    except Exception as e:
        print(f"ERROR: {e}")
