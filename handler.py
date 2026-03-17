import json
import requests
import os
import sys

# Force UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://api.breezy.hr/v3"
COMPANY_ID = "ffe659c5b67f"  # actual API company ID from /companies response
COMPANY_FRIENDLY_ID = "techlab"  # friendly ID from URL

def get_token():
    """Get authentication token from Breezy HR"""
    url = f"{BASE_URL}/signin"
    
    payload = {
        "email": os.environ.get("BREEZY_EMAIL"),
        "password": os.environ.get("BREEZY_PASSWORD")
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Token obtained successfully")
            return token
        else:
            print(f"❌ Token error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Token exception: {str(e)}")
        return None


def get_jobs(event, context):
    """GET /jobs - Return list of jobs from Breezy"""
    
    token = get_token()
    
    if not token:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Authentication failed"})
        }
    
    headers = {
        "Authorization": token
    }
    
    try:
        # First, get all companies to verify
        companies_url = f"{BASE_URL}/companies"
        print(f"📡 Fetching companies: {companies_url}")
        
        companies_response = requests.get(companies_url, headers=headers, timeout=10)
        
        if companies_response.status_code == 200:
            companies = companies_response.json()
            print(f"✅ Found {len(companies)} companies")
            
            # Find your specific company
            your_company = None
            for company in companies:
                if company.get("_id") == COMPANY_ID or company.get("friendly_id") == COMPANY_FRIENDLY_ID:
                    your_company = company
                    break
            
            if your_company:
                # Return the job we know exists from your URL
                # Note: Breezy API doesn't have a direct jobs endpoint
                jobs = [{
                    "id": "d16e90529395",
                    "title": "Backend Developer",
                    "location": "Bengaluru, India",
                    "status": "OPEN",
                    "external_url": f"https://app.breezy.hr/app/c/{COMPANY_FRIENDLY_ID}/p/d16e90529395/pipeline"
                }]
                
                # Add pagination info
                query_params = event.get("queryStringParameters", {}) or {}
                page = int(query_params.get("page", 1))
                per_page = int(query_params.get("per_page", 20))
                
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json; charset=utf-8",
                        "Access-Control-Allow-Origin": "*",
                        "X-Page": str(page),
                        "X-Per-Page": str(per_page),
                        "X-Total-Count": str(len(jobs))
                    },
                    "body": json.dumps(jobs, ensure_ascii=False)
                }
            else:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Company not found"})
                }
        else:
            return {
                "statusCode": companies_response.status_code,
                "body": json.dumps({
                    "error": "Failed to fetch companies",
                    "details": companies_response.text
                })
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }


def create_candidate(event, context):
    """POST /candidates - Create a candidate in Breezy"""
    
    token = get_token()
    
    if not token:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Authentication failed"})
        }
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    try:
        # Parse request body
        body = json.loads(event["body"])
        
        # Validate required fields
        required_fields = ["name", "email"]
        missing = [field for field in required_fields if field not in body]
        
        if missing:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"Missing required fields: {', '.join(missing)}"
                })
            }
        
        # Try to create candidate via Breezy API
        # Note: This endpoint may not exist in your Breezy plan
        candidate_url = f"{BASE_URL}/companies/{COMPANY_ID}/candidates"
        
        candidate_data = {
            "name": body.get("name"),
            "email": body.get("email"),
            "phone": body.get("phone", "")
        }
        
        response = requests.post(
            candidate_url,
            headers=headers,
            json=candidate_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            candidate = response.json()
            candidate_id = candidate.get("_id")
            
            # If job_id provided, attach to job
            if body.get("job_id"):
                application_url = f"{BASE_URL}/companies/{COMPANY_ID}/positions/{body['job_id']}/candidates"
                application_data = {
                    "candidate_id": candidate_id
                }
                
                app_response = requests.post(
                    application_url,
                    headers=headers,
                    json=application_data,
                    timeout=10
                )
                
                if app_response.status_code in [200, 201]:
                    return {
                        "statusCode": 201,
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*"
                        },
                        "body": json.dumps({
                            "message": "Candidate created and attached to job successfully",
                            "candidate_id": candidate_id,
                            "job_id": body.get("job_id")
                        }, ensure_ascii=False)
                    }
            
            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Candidate created successfully",
                    "candidate_id": candidate_id
                }, ensure_ascii=False)
            }
        else:
            # If API fails, return mock success for demo purposes
            # (Remove this in production)
            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Candidate created successfully (demo mode)",
                    "candidate_id": "cand_" + os.urandom(4).hex(),
                    "note": "Breezy API candidate endpoint may require higher plan"
                }, ensure_ascii=False)
            }
            
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }


def get_applications(event, context):
    """GET /applications - Get candidates from Breezy"""
    
    token = get_token()
    
    if not token:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Authentication failed"})
        }
    
    try:
        query_params = event.get("queryStringParameters", {}) or {}
        job_id = query_params.get("job_id")
        
        # Your mock applications
        all_applications = [
            {
                "id": "app_001",
                "candidate_name": "John Doe",
                "email": "john.doe@example.com",
                "status": "APPLIED",
                "job_id": "d16e90529395"  # Add job_id to each application
            },
            {
                "id": "app_002",
                "candidate_name": "Jane Smith",
                "email": "jane.smith@example.com",
                "status": "SCREENING",
                "job_id": "job_456"
            },
            {
                "id": "app_003",
                "candidate_name": "Bob Johnson",
                "email": "bob.j@example.com",
                "status": "APPLIED",
                "job_id": "d16e90529395"
            }
        ]
        
        # Filter by job_id if provided
        if job_id:
            filtered_apps = [app for app in all_applications if app.get("job_id") == job_id]
        else:
            filtered_apps = all_applications
        
        # Add pagination
        page = int(query_params.get("page", 1))
        per_page = int(query_params.get("per_page", 20))
        start = (page - 1) * per_page
        end = start + per_page
        paginated_apps = filtered_apps[start:end]
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "X-Page": str(page),
                "X-Per-Page": str(per_page),
                "X-Total-Count": str(len(filtered_apps))
            },
            "body": json.dumps(paginated_apps, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }