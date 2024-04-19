import requests, json, os

'''
with open('/home/kali/tool/w4af/profiles/full_audit.pw4af', 'r') as file:
    
    data = {'scan_profile': file.read(),
            'target_urls': ['http://192.168.125.129/']}

    response = requests.post('http://127.0.0.1:5000/scans/',
                            data=json.dumps(data),
                            headers={'content-type': 'application/json'})
    
    with open("tmp.html", "w") as tmp:
        print(response.text, file=tmp)
'''

response = requests.get('http://127.0.0.1:5000/scans/0/log')
print(response.text)
response = requests.get('http://127.0.0.1:5000/scans/0/status')
print(response.text)
response = requests.get('http://127.0.0.1:5000/scans/0/kb')
print(response.text)



