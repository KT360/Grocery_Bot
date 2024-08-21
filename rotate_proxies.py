import requests
import concurrent.futures

#The final code assumes all the proxies in the list work

#Remember to only use 'elite' proxies, those actually hide your original ip
proxylist = []

with open('proxies.txt', 'r') as f:
    proxies = f.read().split('\n')
    for proxy in proxies:
        proxylist.append(proxy)


#Should be renamed, this is the code for sending the request to the actual web page you want to scrapoe
def extract_proxy(proxy):
    try:
        r = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https':proxy}, timeout=2)
        print(r.json() + '- working')
    except:
        pass
    return proxy

#This is used to send out requests to a website in parrallel using all the proxies
with concurrent.futures.Executor() as executor:
    executor.map(extract_proxy, proxylist)

