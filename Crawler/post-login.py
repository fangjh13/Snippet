from urllib.request import urlopen, Request
from urllib.parse import urlencode
import lxml.html


url = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example1234@qq.com'
PASSWORD = '123456'


html = urlopen(url).read().decode('utf-8')


def parse_form(html):
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data


data = parse_form(html)
data['email'] = LOGIN_EMAIL
data['password'] = PASSWORD

r = Request(url, data=urlencode(data).encode('utf-8'))
response = urlopen(r)
print(response.geturl())
