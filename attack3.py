import requests

url = "http://localhost:5000/login"

headers = {
    "User-Agent": "python-requests/2.28 AutoHack-Bot"
}

for i in range(20):
    requests.post(url, 
        data={"username": f"user{i}", "password": f"pass{i}"},
        headers=headers)
    print(f"Bot attempt {i}")