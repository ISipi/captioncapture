#!/usr/bin/env python3.7

import random
import requests
from bs4 import BeautifulSoup


def pick_a_header():
    macheader = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.scholar.google.com/',
        'Content-Type': 'text/html; charset=UTF-8',
    }

    linuxheader = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.scholar.google.com/',
        'Content-Type': 'text/html; charset=UTF-8',
    }

    win10header = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.scholar.google.com/',
        'Content-Type': 'text/html; charset=UTF-8',
    }

    win7header = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.scholar.google.com/',
        'Content-Type': 'text/html; charset=UTF-8',

    }

    chromeheader = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.scholar.google.com/',
        'Content-Type': 'text/html; charset=UTF-8',
    }

    headers = [macheader, linuxheader, win7header, win10header, chromeheader]

    final_header = random.choice(headers)

    return final_header


def get_proxies():
    """
    Function from: https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
    :return:
    """

    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = BeautifulSoup(response.content, 'lxml')
    proxies = []
    body = parser.find('tbody')

    for i in body.find_all('tr'):
        first_child = i.find("td", recursive=False)
        ip_address = first_child.text
        port = first_child.findNext()
        code = port.findNext()
        country = code.findNext()
        anonymity = country.findNext()
        if "elite proxy" in anonymity.text:
            proxy = f"http://{ip_address}:{port.text}"
            proxies.append(proxy)
    final_proxy = random.choice(proxies)
    #print(final_proxy)
    return final_proxy
