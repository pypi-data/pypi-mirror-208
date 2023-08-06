import requests

def fanbook_request(key, api, method, json_data):
    """
    发送fanbook HTTP请求并返回API返回的数据。

    参数：
    key (str)：机器人令牌。
    api (str)：API的名称。
    method (str)：请求方法，如"POST"或"GET"。
    json_data (dict)：要发送的JSON数据。

    返回：
    response_data (dict)：API返回的数据，如果请求失败则返回None。
    """
    url = f"https://a1.fanbook.mobi/api/bot/{key}/{api}"
    headers = {'Content-Type': 'application/json'}
    response = requests.request(method, url, json=json_data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        return None

