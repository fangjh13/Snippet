from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlencode
import lxml.html
from io import BytesIO
from base64 import b64decode
from PIL import Image
import pytesseract


def parse_form(html):
    tree = lxml.html.fromstring(html)
    form = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            form[e.get('name')] = e.get('value')
    return form
    
def get_captcha(html):
    tree = lxml.html.fromstring(html)
    src = tree.cssselect('div#recaptcha img')[0].get('src').split(',')[-1]
    img = Image.open(BytesIO(b64decode(src)))
    return img

# url = 'http://example.webscraping.com/places/default/user/register'
# cj = CookieJar()
# opener = build_opener(HTTPCookieProcessor(cj))
# register_page = opener.open(url)
# html = register_page.read()

# form = parse_form(html)
# print(form)
# img = get_captcha(html)
# img.save('temp.jpg')
# gray = img.convert('L')
# gray.save('temp2.jpg')
# bw = gray.point(lambda x: x if x < 1 else 255, '1')
# bw.save('temp3.jpg')


# print(pytesseract.image_to_string(bw))

def register(first_name, last_name, email, password):
    # get register page
    url = 'http://example.webscraping.com/places/default/user/register'
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))
    html = opener.open(url).read()

    # try recognize captcha
    img = get_captcha(html)
    gray = img.convert('L')
    bw = gray.point(lambda x: x if x < 1 else 255, '1')
    captcha = pytesseract.image_to_string(bw)

    # parse form and fill
    form = parse_form(html)
    form['first_name'] = first_name
    form['last_name'] = last_name
    form['email'] = email
    form['password'] = password
    form['password_two'] = password
    form['recaptcha_response_field'] = captcha

    data = urlencode(form).encode('utf-8')
    r = Request(url=url, data=data)
    register_page = opener.open(r)
    return '/user/register' not in register_page.geturl()

print(register('test_fang', 'test', 'example12345@qq.com', '123456'))