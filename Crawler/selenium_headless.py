from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# chrome headless mode config
chrome_options = Options()
chrome_options.add_argument("headless")
chrome_options.add_argument('window-size=800x841')
chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'


def get_page_source(url, page=1, retries=3):
    # use PhantomJS deprecated
    # SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
    # driver = webdriver.PhantomJS(service_args=SERVICE_ARGS)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    if retries > 0:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        try:
            # 跳到指定页数
            if page > 1:
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                        '#mainsrp-pager > div > div > div > div.form > input'))
                    )
                element.clear()
                element.send_keys(page)
                submit = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                        '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
                    )
                submit.click()
            wait.until(
                EC.presence_of_all_elements_located((By.XPATH,
                    '//*[@class="item J_MouserOnverReq  "]'))
                )
            return driver.page_source
        except TimeoutException:
            get_page_source(url, page=page, retries=retries-1)
        finally:
            driver.close()
    else:
        return

print(get_page_source('https://s.taobao.com/search?q=iphone', page=10))