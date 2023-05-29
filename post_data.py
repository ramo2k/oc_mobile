import requests
import json

url = "https://post-get-function.azurewebsites.net/api/HttpTriggerPostGet?code=LE986-5gmHqILUL_p-DQ1SXhbDatNS_E5Pp-QPj5YtYGAzFuVc0AHw=="

data = {
    'is_open' : None,
    'pourcentage_input' : None,
    'alert' : None,
    'temperature' : None,
    'pourcentage_ouverture_porte' : None,
    'distance_porte' : None,
}

headers = {'Content-type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)

if response.status_code == 200:
    print(response.text)
else:
    print(f"Error: Received status code {response.status_code}")
