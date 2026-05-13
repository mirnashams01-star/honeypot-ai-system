import requests

url = "http://localhost:5000/login"

passwords = ["123456", "password", "admin123", "qwerty", 
             "abc123", "111111", "letmein", "monkey"]

for pwd in passwords:
    requests.post(url, data={"username": "admin", "password": pwd})
    print(f"Tried: {pwd}")