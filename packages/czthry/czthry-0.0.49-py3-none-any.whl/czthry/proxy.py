import json
import random


rawdata = [
    {"ip": "8.208.85.34", "port": "8080", "protocol": "HTTPS"},
    {"ip": "8.208.90.194", "port": "808", "protocol": "HTTPS"},
    {"ip": "8.208.90.243", "port": "443", "protocol": "HTTPS"},
    {"ip": "8.219.169.172", "port": "8080", "protocol": "HTTPS"},
    {"ip": "8.213.128.6", "port": "5566", "protocol": "HTTPS"},
    {"ip": "45.15.16.179", "port": "8118", "protocol": "HTTPS"},
    {"ip": "111.175.84.171", "port": "8118", "protocol": "HTTP"},
    {"ip": "43.132.147.145", "port": "14002", "protocol": "HTTPS"},
    {"ip": "121.196.152.42", "port": "80", "protocol": "HTTP"},
    {"ip": "131.196.244.140", "port": "999", "protocol": "HTTP"},
    {"ip": "123.182.58.216", "port": "8089", "protocol": "HTTPS"},
    {"ip": "114.86.181.93", "port": "9000", "protocol": "HTTPS"},
    {"ip": "121.33.160.12", "port": "808", "protocol": "HTTP"},
    {"ip": "27.11.178.227", "port": "8118", "protocol": "HTTP"},
    {"ip": "49.86.67.144", "port": "8118", "protocol": "HTTP"},
    {"ip": "49.0.255.127", "port": "3128", "protocol": "HTTPS"},
    {"ip": "120.46.180.194", "port": "9091", "protocol": "HTTP"},
    {"ip": "123.115.64.2", "port": "9000", "protocol": "HTTP"},
    {"ip": "114.86.181.92", "port": "9000", "protocol": "HTTPS"},
    {"ip": "112.35.127.238", "port": "3128", "protocol": "HTTPS"},
    {"ip": "119.23.110.63", "port": "8085", "protocol": "HTTP"},
    {"ip": "94.74.123.148", "port": "3128", "protocol": "HTTPS"},
    {"ip": "114.43.143.52", "port": "3128", "protocol": "HTTP"},
    {"ip": "49.0.252.39", "port": "8080", "protocol": "HTTPS"},
    {"ip": "47.91.126.36", "port": "8080", "protocol": "HTTP"},
    {"ip": "202.21.115.94", "port": "44574", "protocol": "HTTP"},
    {"ip": "115.226.131.193", "port": "8888", "protocol": "HTTP"},
    {"ip": "111.225.153.237", "port": "8089", "protocol": "HTTPS"},
    {"ip": "111.225.153.241", "port": "8089", "protocol": "HTTPS"},
    {"ip": "123.182.59.175", "port": "8089", "protocol": "HTTPS"},
    {"ip": "120.77.172.30", "port": "8118", "protocol": "HTTP"},
    {"ip": "111.225.153.76", "port": "8089", "protocol": "HTTP"},
    {"ip": "218.86.60.18", "port": "4145", "protocol": "HTTP"},
    {"ip": "111.225.153.102", "port": "8089", "protocol": "HTTP"},
    {"ip": "39.108.230.16", "port": "3128", "protocol": "HTTP"},
    {"ip": "221.224.213.156", "port": "1080", "protocol": "HTTP"},
    {"ip": "43.228.131.115", "port": "32992", "protocol": "HTTP"},
    {"ip": "218.21.78.35", "port": "4145", "protocol": "HTTP"},
    {"ip": "140.206.81.178", "port": "1080", "protocol": "HTTP"},
    {"ip": "80.80.164.164", "port": "10801", "protocol": "HTTP"},
    {"ip": "222.83.251.211", "port": "4145", "protocol": "HTTP"},
    {"ip": "61.148.199.206", "port": "4145", "protocol": "HTTP"},
    {"ip": "203.184.132.153", "port": "8118", "protocol": "HTTP"},
    {"ip": "80.80.167.18", "port": "10801", "protocol": "HTTP"},
    {"ip": "183.251.50.152", "port": "4145", "protocol": "HTTP"},
    {"ip": "218.64.122.99", "port": "7302", "protocol": "HTTP"},
    {"ip": "210.61.216.66", "port": "33990", "protocol": "HTTP"},
    {"ip": "58.39.62.145", "port": "9797", "protocol": "HTTP"},
    {"ip": "117.94.124.21", "port": "9000", "protocol": "HTTP"},
    {"ip": "202.43.190.11", "port": "8118", "protocol": "HTTP"},
    {"ip": "36.66.19.10", "port": "8080", "protocol": "HTTP"},
    {"ip": "115.29.170.58", "port": "8118", "protocol": "HTTP"},
    {"ip": "74.208.177.198", "port": "80", "protocol": "HTTP"},
    {"ip": "221.5.80.66", "port": "3128", "protocol": "HTTPS"},
    {"ip": "61.182.213.83", "port": "7302", "protocol": "HTTP"},
    {"ip": "47.108.137.58", "port": "33080", "protocol": "HTTP"},
    {"ip": "8.210.187.30", "port": "8888", "protocol": "HTTP"},
    {"ip": "111.225.152.159", "port": "8089", "protocol": "HTTP"},
    {"ip": "123.119.25.121", "port": "8000", "protocol": "HTTP"},
    {"ip": "119.12.168.222", "port": "443", "protocol": "HTTP"},
    {"ip": "39.106.16.117", "port": "80", "protocol": "HTTPS"},
    {"ip": "120.24.76.81", "port": "8123", "protocol": "HTTPS"},
    {"ip": "220.179.90.8", "port": "38888", "protocol": "HTTP"},
    {"ip": "45.94.209.80", "port": "3128", "protocol": "HTTPS"},
    {"ip": "111.225.152.132", "port": "8089", "protocol": "HTTP"},
    {"ip": "222.67.96.23", "port": "9000", "protocol": "HTTP"},
    {"ip": "112.232.110.109", "port": "8118", "protocol": "HTTP"},
    {"ip": "47.75.166.66", "port": "3128", "protocol": "HTTPS"},
    {"ip": "47.75.127.149", "port": "8888", "protocol": "HTTPS"},
    {"ip": "103.146.196.24", "port": "8080", "protocol": "HTTP"},
    {"ip": "222.129.139.161", "port": "9000", "protocol": "HTTPS"},
    {"ip": "180.102.178.110", "port": "8118", "protocol": "HTTP"},
    {"ip": "47.99.154.225", "port": "8081", "protocol": "HTTP"},
    {"ip": "124.167.208.183", "port": "8118", "protocol": "HTTP"},
    {"ip": "116.7.8.80", "port": "9000", "protocol": "HTTPS"},
    {"ip": "27.46.46.105", "port": "8888", "protocol": "HTTPS"},
    {"ip": "39.101.202.89", "port": "3128", "protocol": "HTTP"},
    {"ip": "123.112.240.240", "port": "8118", "protocol": "HTTP"},
    {"ip": "118.178.121.234", "port": "5000", "protocol": "HTTPS"},
    {"ip": "103.75.117.21", "port": "4443", "protocol": "HTTP"},
    {"ip": "117.80.10.23", "port": "888", "protocol": "HTTP"},
    {"ip": "111.225.153.69", "port": "8089", "protocol": "HTTPS"},
    {"ip": "180.119.93.220", "port": "8888", "protocol": "HTTP"},
    {"ip": "180.156.203.60", "port": "8001", "protocol": "HTTP"},
    {"ip": "111.225.152.36", "port": "8089", "protocol": "HTTP"},
    {"ip": "1.168.218.150", "port": "3128", "protocol": "HTTPS"},
    {"ip": "47.242.37.241", "port": "3128", "protocol": "HTTPS"},
    {"ip": "190.89.37.75", "port": "999", "protocol": "HTTPS"},
    {"ip": "125.65.40.199", "port": "12345", "protocol": "HTTP"},
    {"ip": "111.225.153.98", "port": "8089", "protocol": "HTTP"},
    {"ip": "114.240.226.200", "port": "808", "protocol": "HTTPS"},
    {"ip": "114.230.23.23", "port": "8118", "protocol": "HTTP"},
    {"ip": "47.109.51.138", "port": "80", "protocol": "HTTP"},
    {"ip": "112.91.139.217", "port": "8000", "protocol": "HTTP"},
    {"ip": "110.83.249.38", "port": "9091", "protocol": "HTTP"},
    {"ip": "39.99.227.194", "port": "7777", "protocol": "HTTP"},
    {"ip": "223.166.186.230", "port": "7890", "protocol": "HTTPS"},
    {"ip": "47.113.127.67", "port": "3128", "protocol": "HTTP"},
    {"ip": "175.6.97.188", "port": "9128", "protocol": "HTTP"},
    {"ip": "27.46.55.3", "port": "9797", "protocol": "HTTP"}
]


_proxies = {}


def get_proxy(url):
    global _proxies
    if not _proxies:
        _proxies['http'] = list(filter(lambda it:it['protocol'] == 'HTTPS', rawdata))
        _proxies['https'] = list(filter(lambda it:it['protocol'] == 'HTTP', rawdata))
    protocol = url.split(':')[0].lower()
    proxy = random.choice(_proxies[protocol])
    proxy_protocol = proxy['protocol'].lower()
    proxy_ip = proxy['ip']
    proxy_port = proxy['port']
    proxies = {proxy_protocol: '{}://{}:{}'.format(proxy_protocol, proxy_ip, proxy_port)}
    return proxies


if __name__ == '__main__':
    p = get_proxy('http://www.xxx.com')
    print(p)
    pass