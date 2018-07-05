from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
import lxml.html
import requests


url = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example1234@qq.com'
PASSWORD = '123456'

# cj = CookieJar()
# opener = build_opener(HTTPCookieProcessor(cj))

# html = opener.open(url).read().decode('utf-8')


def parse_form(html):
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data


# data = parse_form(html)
# data['email'] = LOGIN_EMAIL
# data['password'] = PASSWORD


# r = Request(url, data=urlencode(data).encode('utf-8'))
# response = opener.open(r)
# print(response.geturl())
r =  requests.Session()
html = r.get(url).text
data = parse_form(html)
data['email'] = LOGIN_EMAIL
data['password'] = PASSWORD
result = r.post(url, data=data)
print(result.url)
