import urllib.request
print(urllib.request.urlopen('http://localhost:5000/api/admin/calculations/1').read().decode())
