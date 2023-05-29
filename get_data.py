import requests

url = "https://post-get-function.azurewebsites.net/api/HttpTriggerPostGet?code=LE986-5gmHqILUL_p-DQ1SXhbDatNS_E5Pp-QPj5YtYGAzFuVc0AHw=="

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    is_open = data.get('is_open')
    pourcentage_input = data.get('pourcentage_input')
    print(is_open)
    print(pourcentage_input)
    print(data)
else:
    print(f"Error: Received status code {response.status_code}")
