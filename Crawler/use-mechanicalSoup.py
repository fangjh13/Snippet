import mechanicalsoup

url = 'http://example.webscraping.com/places/default/user/login'
country_url = 'http://example.webscraping.com/places/default/edit/Armenia-12'
LOGIN_EMAIL = 'example1234@qq.com'
PASSWORD = '123456'


browser = mechanicalsoup.StatefulBrowser()
browser.open(url)

browser.select_form(nr=0)
browser["email"] = LOGIN_EMAIL
browser['password'] = PASSWORD
browser.submit_selected()

browser.open(country_url)

browser.select_form(nr=0)
page = browser.get_current_page()
p = page.find('form').find('input', id='places_population')['value']
browser['population'] = str(int(p) + 100)
browser.submit_selected()
