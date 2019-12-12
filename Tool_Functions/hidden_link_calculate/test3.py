import json
testOpen = open("test.json")
testV = json.loads(testOpen.read())
print(len(testV))