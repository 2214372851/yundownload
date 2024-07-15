import requests

# proxy = '117.42.94.219:21472'
proxy = '106.105.218.244:80'
proxies = {
    'http': 'http://' + proxy,
    'https': 'http://' + proxy,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}
r = requests.get('https://www.baidu.com/', proxies=proxies, headers=headers, timeout=5, verify=False)
print(r.status_code)
print(r.text)
