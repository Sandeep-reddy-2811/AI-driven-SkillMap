import requests
import json

url = "http://127.0.0.1:8000/api/analyze/"

print("Sending request to:", url)
print("=" * 50)

with open("resume.pdf", "rb") as resume, \
     open("job_description.pdf", "rb") as jd:

    files = {
        "resume": ("resume.pdf", resume, "application/pdf"),
        "job_description": ("job_description.pdf", jd, "application/pdf"),
    }

    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("=" * 50)

try:
    data = response.json()
    print(json.dumps(data, indent=2))
except:
    print("Raw response:", response.text)