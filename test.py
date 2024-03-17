import requests

cookies = {
    '_ga': 'GA1.1.670127090.1710580121',
    '__stripe_mid': '46de4a30-44dc-4b36-9b69-6352a8de82977bb23e',
    '__stripe_sid': 'fbd11e2e-c22a-4a53-afed-c22fbd137979760d92',
    'token': 'DldOYyTeAKQeWVyORNWOJtfTGQbSqzubrBeSYsYhjOtkygneKFUdpDLHUOvVHjYDSyuCwDKCZviHubWkTnbmLLsPDbDaUwKLziDCVWQdRZozkmuUgJeECPqjVMMjpjDt',
    'token': 'DldOYyTeAKQeWVyORNWOJtfTGQbSqzubrBeSYsYhjOtkygneKFUdpDLHUOvVHjYDSyuCwDKCZviHubWkTnbmLLsPDbDaUwKLziDCVWQdRZozkmuUgJeECPqjVMMjpjDt',
    'aws-waf-token': '4a4efae5-b563-428f-b85f-8bbbfd98a499:AQoAbANAjREBAAAA:YLxEOBCcxdN8ws0rejvtqXJ0B2nSqq96kO+gQnOBd+7JMcl4HmBysg5zb9TjyZ3ENEkfHBowtsxHPYP+gyNy6rMkpYTKKdz3yctqyqQAw9902EnLyuX/culmkmP3mA71+uYb39Ax+kzeA0WuwuJDy75ZZR9M8GdBin+mRlOSyRdDAmxerjQJtXVpFi6n9mABYAp59TxmsW8cA0Yczvz2HCpWPQFSIRknHFJjj5kS/7dCGZTfykcuJbR1csEHauqzjGCelxs=',
    '_ga_8Q63TH4CSL': 'GS1.1.1710580120.1.1.1710580304.37.0.0',
    'hf-chat': '7bf1c2d1-af02-4a02-8cd5-f4ccc6c4f31d',
}

headers = {
    'authority': 'huggingface.co',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'content-type': 'application/json',
    # 'cookie': '_ga=GA1.1.670127090.1710580121; __stripe_mid=46de4a30-44dc-4b36-9b69-6352a8de82977bb23e; __stripe_sid=fbd11e2e-c22a-4a53-afed-c22fbd137979760d92; token=DldOYyTeAKQeWVyORNWOJtfTGQbSqzubrBeSYsYhjOtkygneKFUdpDLHUOvVHjYDSyuCwDKCZviHubWkTnbmLLsPDbDaUwKLziDCVWQdRZozkmuUgJeECPqjVMMjpjDt; token=DldOYyTeAKQeWVyORNWOJtfTGQbSqzubrBeSYsYhjOtkygneKFUdpDLHUOvVHjYDSyuCwDKCZviHubWkTnbmLLsPDbDaUwKLziDCVWQdRZozkmuUgJeECPqjVMMjpjDt; aws-waf-token=4a4efae5-b563-428f-b85f-8bbbfd98a499:AQoAbANAjREBAAAA:YLxEOBCcxdN8ws0rejvtqXJ0B2nSqq96kO+gQnOBd+7JMcl4HmBysg5zb9TjyZ3ENEkfHBowtsxHPYP+gyNy6rMkpYTKKdz3yctqyqQAw9902EnLyuX/culmkmP3mA71+uYb39Ax+kzeA0WuwuJDy75ZZR9M8GdBin+mRlOSyRdDAmxerjQJtXVpFi6n9mABYAp59TxmsW8cA0Yczvz2HCpWPQFSIRknHFJjj5kS/7dCGZTfykcuJbR1csEHauqzjGCelxs=; _ga_8Q63TH4CSL=GS1.1.1710580120.1.1.1710580304.37.0.0; hf-chat=7bf1c2d1-af02-4a02-8cd5-f4ccc6c4f31d',
    'origin': 'https://huggingface.co',
    'referer': 'https://huggingface.co/chat/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
}

json_data = {
    'model': 'openchat/openchat-3.5-0106',
    'preprompt': '',
}

response = requests.post('https://huggingface.co/chat/conversation', cookies=cookies, headers=headers, json=json_data)
print(response.content)
# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"model":"openchat/openchat-3.5-0106","preprompt":""}'
#response = requests.post('https://huggingface.co/chat/conversation', cookies=cookies, headers=headers, data=data)