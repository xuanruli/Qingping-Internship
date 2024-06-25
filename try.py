import requests

url = 'https://www.iwencai.com/customized/chart/get-robot-data'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '320',
    'Content-Type': 'application/json',
    'Cookie': 'other_uid=Ths_iwencai_Xuangu_id9gpdismkkeo4fov5w6adcff04pwa5k; ta_random_userid=oupcwwvefd; etc.',
    'Host': 'www.iwencai.com',
    'Origin': 'https://www.iwencai.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.iwencai.com/unifiedwap/result?w=%E6%B2%AA%E6%B7%B1300&querytype=stock',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

data = {
    "question": "沪深300",
    "rewriteQuestion": "沪深300",
    "q": "沪深300",
    "domain": "abs_股票领域",
    "query": "沪深300",
    "iwc_sort_info": {
        "sortKey": "股票市场类型",
        "sortType": "desc",
        "sortFrom": "Original",
        "sortQuery": True
    }
}

response = requests.post(url, headers=headers,json = data)

print(response.headers)
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:500]}")

try:
    response_data = response.json()
    print("JSON Data:", response_data)

    datas = response_data.get('datas', [])
    for item in datas:
        print(f"Code: {item.get('code')}, Name: {item.get('股票简称')}, Price: {item.get('最新价')}")

except requests.exceptions.JSONDecodeError:
    print("Error: The response is not in JSON format.")