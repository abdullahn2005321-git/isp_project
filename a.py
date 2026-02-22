import json

# 1) نص JSON
s = '{"name":"Abdullah","skills":["python","sql"],"active":true}'
# ملاحظة: true في JSON لازم تتحول لـ True في بايثون بعد loads

data = json.loads(s)
print(data)
print(type(data))
print(data["skills"][0])

# 2) رجعنا نحوله لنص
s2 = json.dump(data)
print(s2)
print(type(s2))

data2 = json.loads(s2)
print(data2)
print(type(data2))