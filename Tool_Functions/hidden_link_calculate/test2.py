import requests
import json
url = 'http://127.0.0.1:2223/putData'
testOpen = json.loads(open("test.json").read())

r = requests.post(url, json=testOpen).text
print(r)