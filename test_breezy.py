import requests
import json

email = input("Enter your Breezy email: ")
password = input("Enter your Breezy password: ")

print("\n🔑 Getting token...")
auth_res = requests.post(
    "https://api.breezy.hr/v3/signin",
    json={"email": email, "password": password}
)

if auth_res.status_code != 200:
    print(f"❌ Auth failed: {auth_res.text}")
    exit()

token = auth_res.json()["access_token"]
print(f"✅ Token received: {token[:20]}...")

headers = {"Authorization": token}

# Test various endpoints
endpoints = [
    "/companies",
    "/companies/techlab",
    "/companies/techlab/positions",
    "/companies/techlab/jobs",
    "/positions",
    "/jobs",
    "/me",
    "/account"
]

print("\n🔍 Testing Breezy API endpoints...")
for endpoint in endpoints:
    url = f"https://api.breezy.hr/v3{endpoint}"
    print(f"\n📡 Testing: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Response: {json.dumps(data)[:200]}...")
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")