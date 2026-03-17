import requests
import os
import json

email = input("Enter your Breezy email: ")
password = input("Enter your Breezy password: ")

# Get token
print("\n🔑 Getting token...")
auth_res = requests.post(
    "https://api.breezy.hr/v3/signin",
    json={"email": email, "password": password}
)

if auth_res.status_code != 200:
    print(f"❌ Auth failed: {auth_res.text}")
    exit()

token = auth_res.json()["access_token"]
print(f"✅ Token received")

headers = {"Authorization": token}

# Try different endpoints to find what works
print("\n📡 Testing different endpoints...")

endpoints = [
    "/companies",
    "/positions",
    "/me",
    "/company",
    "/account"
]

for endpoint in endpoints:
    url = f"https://api.breezy.hr/v3{endpoint}"
    print(f"\n🔍 Trying: {url}")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {res.status_code}")
        if res.status_code == 200:
            print(f"   ✅ Works! Response preview: {json.dumps(res.json())[:200]}")
        else:
            print(f"   ❌ Failed: {res.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")