```markdown
# ATS Integration Microservice - Breezy HR

# Overview
Serverless microservice that integrates with Breezy HR API to provide unified endpoints for jobs and candidates. Built with Python and Serverless Framework.

Base URL: http://localhost:3000

# Features
- GET /jobs - Return list of open jobs from Breezy HR
- POST /candidates - Accept candidate payload and create in Breezy HR
- GET /applications - List applications for a given job
- Pagination support with page/per_page parameters
- JSON error responses
- Serverless offline support for local testing

# Prerequisites
- Node.js v14 or higher
- Python 3.10 or higher
- Serverless Framework: npm install -g serverless
- Breezy HR account (free tier)

# Breezy HR Setup

1. Create an account at https://breezy.hr/signup
2. Create a company (e.g., "TechLab")
3. Create and publish a test job (e.g., "Backend Developer")
4. Note your Job ID from the URL: https://app.breezy.hr/app/c/techlab/p/[JOB_ID]/pipeline
5. Get your Company ID by running:

   curl -X POST https://api.breezy.hr/v3/signin \
     -H "Content-Type: application/json" \
     -d '{"email":"your-email","password":"your-password"}'

   Then use the token:
   curl -H "Authorization: your-token" https://api.breezy.hr/v3/companies

   Your company _id (e.g., ffe659c5b67f) is what you need.

# Installation

1. Create a new serverless project:
   serverless create --template aws-python --path ats-microservice
   cd ats-microservice

2. Install dependencies:
   pip install requests
   npm install --save-dev serverless-offline

3. Create requirements.txt:
   echo "requests==2.31.0" > requirements.txt

# Configuration

Set environment variables with your Breezy HR credentials:

Windows CMD:
   set BREEZY_EMAIL=your-email@example.com
   set BREEZY_PASSWORD=your-password

PowerShell:
   $env:BREEZY_EMAIL="youremail@exm.com"
   $env:BREEZY_PASSWORD="yourpassword"

# Serverless Configuration

Create serverless.yml:

service: ats-microservice

provider:
  name: aws
  runtime: python3.10
  timeout: 30
  environment:
    BREEZY_EMAIL: ${env:BREEZY_EMAIL}
    BREEZY_PASSWORD: ${env:BREEZY_PASSWORD}

plugins:
  - serverless-offline

custom:
  serverless-offline:
    httpPort: 3000
    lambdaPort: 3003
    noPrependStageInUrl: true

functions:
  getJobs:
    handler: handler.get_jobs
    events:
      - http:
          path: jobs
          method: get

  createCandidate:
    handler: handler.create_candidate
    events:
      - http:
          path: candidates
          method: post

  getApplications:
    handler: handler.get_applications
    events:
      - http:
          path: applications
          method: get

# Running Locally

Start the server:
   serverless offline

The API will be available at http://localhost:3000

# API Documentation

# GET /jobs

Fetch all open jobs from Breezy HR.

Query Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 20)

Example:
   curl http://localhost:3000/jobs?page=1&per_page=10

Response:
   [
     {
       "id": "d16e90529395",
       "title": "Backend Developer",
       "location": "Bengaluru, India",
       "status": "OPEN",
       "external_url": "https://app.breezy.hr/app/c/techlab/p/d16e90529395/pipeline"
     }
   ]

# POST /candidates

Submit a new candidate to the ATS.

Headers: Content-Type: application/json

Request Body:
   {
     "name": "Claire lee",
     "email": "claire@example.com",
     "phone": "1234567899",
     "job_id": "d16e90529395"
   }

Example:
   curl -X POST http://localhost:3000/candidates \
     -H "Content-Type: application/json" \
     -d "{\"name\":\"claire lee\",\"email\":\"claire@example.com\",\"phone\":\"1234567899\",\"job_id\":\"d16e90529395\"}"

Response:
   {
     "message": "Candidate created successfully (demo mode)",
     "candidate_id": "cand_8d1d2e09"
   }

# GET /applications

Retrieve applications, optionally filtered by job.

Query Parameters:
- job_id: Filter by job ID
- page: Page number (default: 1)
- per_page: Items per page (default: 20)

Example:
   curl "http://localhost:3000/applications?job_id=d16e90529395&page=1&per_page=20"

Response:
   [
     {
       "id": "app_001",
       "candidate_name": "claire lee",
       "email": "clair.doe@example.com",
       "status": "APPLIED"
     },
     {
       "id": "app_003",
       "candidate_name": "Bob lee",
       "email": "bob.j@example.com",
       "status": "APPLIED"
     }
   ]

# Error Handling

All endpoints return appropriate HTTP status codes and JSON error messages:

- 200: Success
- 201: Created
- 400: Bad Request (missing parameters)
- 401: Unauthorized (authentication failed)
- 404: Not Found (invalid endpoint)
- 500: Internal Server Error

Example error response for invalid route:
   {
     "error": "Not Found",
     "statusCode": 404
   }

# Pagination

All GET endpoints support pagination with response headers:
- X-Page: Current page number
- X-Per-Page: Items per page
- X-Total-Count: Total number of items

# Project Structure

ats-microservice/
├── handler.py          # Main application code
├── serverless.yml      # Serverless configuration
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
└── README.md          # This file

# Troubleshooting

1. Port already in use:
   Error: EADDRINUSE: address already in use
   Solution: Change lambdaPort in serverless.yml to 3003 or 3004

2. Authentication failed:
   Check that BREEZY_EMAIL and BREEZY_PASSWORD are set correctly

3. No jobs returned:
   Ensure you have created and published at least one job in Breezy HR

4. Filter not working:
   Verify that job_id in your applications matches the one you're filtering by

# License

This project is created for educational purposes.
```