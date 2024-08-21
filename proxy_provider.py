#!/usr/bin/env python

import sys
import urllib.request
import ssl

class AppURLopener(urllib.request.FancyURLopener):
    version = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


print('If you get error "ImportError: No module named \'six\'" install six:\n' + \
    '$ sudo pip install six\n\n')

#Bright Data Access
brd_user = 'hl_47a7b1c8'
brd_zone = 'residential_proxy1'
brd_passwd = '10gaf9vj34tc'
brd_superpoxy = 'brd.superproxy.io:22225'
brd_connectStr = 'brd-customer-' + brd_user + '-zone-' + brd_zone + ':' + brd_passwd + '@' + brd_superpoxy

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Switch between brd_test_url to get a json instead of txt response: 
#brd_test_url = 'https://geo.brdtest.com/mygeo.json'
#brd_test_url = 'https://foodbasics.ca/'

# Load the CA certificate file
ca_cert_path = r'C:\Users\kamto\Documents\ca.crt'
context = ssl.create_default_context(cafile=ca_cert_path)

if sys.version_info[0] == 2:
    import six
    from six.moves.urllib import request
    opener = request.build_opener(
        request.ProxyHandler(
            {'http': 'http://' + brd_connectStr,
            'https': 'https://' + brd_connectStr }),
        request.HTTPSHandler(context=context)
    )
    print(opener.open(brd_test_url).read())
elif sys.version_info[0] == 3:
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {'http': 'http://' + brd_connectStr,
            'https': 'https://' + brd_connectStr }),
        urllib.request.HTTPSHandler(context=context)
    )

    # Build a Request object with the user agent header
    request = urllib.request.Request(
        url='https://geo.brdtest.com/mygeo.json',
        headers={'User-Agent': user_agent}
    )

    response = opener.open(request)
    print(response.read())