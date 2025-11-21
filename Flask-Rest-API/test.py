import requests

BASE = "http://127.0.0.1:5000/"

# response = requests.get("https://google.com")
response = requests.put(BASE + "video/2", {"name": "A", "views": 10, "likes": 10} )
# response = requests.patch(BASE + "video/2", {"name": "A", "views": 10, "likes": 10})
print(response.json())
res = requests.delete(BASE + "video/1")
# print(res.json())
response = requests.get(BASE + "video/1")
print(response.json())
response = requests.get(BASE + "video/2")
print(response.json())