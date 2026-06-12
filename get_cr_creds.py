import urllib.request
import json
import base64

CLIENT_ID = "f7955861-3ef1-4dd9-8204-603ec0c7ecb2"
CLIENT_SECRET = "272792c7-d5eb-4fdc-8fbd-fdc316b88c70"
IAM_TOKEN_URL = "https://iam.api.vngcloud.vn/accounts-api/v2/auth/token"
CR_CRED_URL = "https://agentbase.api.vngcloud.vn/cr/api/v1/registry-credential"

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

def get_credentials(token):
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(CR_CRED_URL, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

if __name__ == "__main__":
    try:
        token = get_token()
        creds = get_credentials(token)
        print(f"USER={creds.get('username')}")
        print(f"SECRET={creds.get('secret')}")
    except Exception as e:
        print(f"ERROR: {e}")
