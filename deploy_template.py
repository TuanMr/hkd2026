import urllib.request
import json
import base64

CLIENT_ID = "f7955861-3ef1-4dd9-8204-603ec0c7ecb2"
CLIENT_SECRET = "272792c7-d5eb-4fdc-8fbd-fdc316b88c70"
IAM_TOKEN_URL = "https://iam.api.vngcloud.vn/accounts-api/v2/auth/token"
RUNTIME_URL = "https://agentbase.api.vngcloud.vn/runtime"

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

def create_runtime(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "hkd-2026",
        "flavorId": "runtime-s2-general-4x8",
        "image": "vcr.vngcloud.vn/openclaw-templates/python-general:latest",
        "env": {
            "LLM_API_KEY": "vn--PoOQb4bSM_OCNWV06HW8z8Sw96_dA36cbc0b0d5df4275815569f570ed3deb2I-6PzcuZnmEzAH9h_qd-d_zuT0IsOH",
            "MEMORY_ID": "memory-87f247fb-320a-48a5-a8db-ded93704ec9a"
        }
    }
    
    req = urllib.request.Request(
        RUNTIME_URL, 
        data=json.dumps(payload).encode(), 
        headers=headers, 
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

if __name__ == "__main__":
    token = get_token()
    result = create_runtime(token)
    print(json.dumps(result, indent=2, ensure_ascii=False))
