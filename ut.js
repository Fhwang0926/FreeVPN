import requests


rs = requests.get("https://www.google.com")
print(rs.status_code)
	