import time
import json
import hashlib
import random
import requests

# class APIClient:
#     def __init__(self, base_url):
#         self.base_url = base_url

#     def post(self, endpoint, data):
#         url = f"{self.base_url}/{endpoint}"
#         response = requests.post(url, json=data)
#         return response.json()

    # 签名对象
getSha256 = lambda content: hashlib.sha256(content.encode("utf-8")).hexdigest()

# 密钥信息获取与帮助文档：https://www.aigcaas.cn/article/16.html

secret_id = 'MzVScjKLAQohekq'  # 密钥信息
secret_key = 'uoYhZTJfnNAawbw'  # 密钥信息
application_name = 'modi'  # 应用名称
api_name = 'modi'  # 接口名称

# 请求地址
url = "https://api.aigcaas.cn/product/%s/api/%s" % (application_name, api_name)
# 构建请求头
nonce = str(random.randint(1, 10000))
timestamp = str(int(time.time()))
token = getSha256(("%s%s%s" % (timestamp, secret_key, nonce)))
headers = {
    'SecretID': secret_id,
    'Nonce': nonce,
    'Token': token,
    'Timestamp': timestamp,
    'Content-Type': 'application/json'
}
# 构建请求 body
data = {
    "text": "a cute baby",
    "width": 512,
    "height": 512,
    "negative_prompt":"human",
    "num_inference_steps":40
}

# 获取响应
response = requests.request("POST", url, headers=headers, data=json.dumps(data))
print(response.text)

# 如果是流式响应，可以参考下面的代码
# response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
# for chunk in response.iter_content():
#      if chunk:
#          print(chunk)