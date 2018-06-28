from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *

url = 'http://example.webscraping.com/places/default/search'
app = QApplication([])
webview = QWebView()
loop = QEventLoop()
webview.loadFinished.connect(loop.quit)
webview.load(QUrl(url))
loop.exec_()
webview.show()
frame = webview.page().mainFrame()
frame.findFirstElement('#search_term').setAttribute('value', '.')
frame.findFirstElement('#page_size option:checked').setPlainText('1000')
frame.findFirstElement('#search').evaluateJavaScript('this.click()')
# app.exec_()
elements = None
while not elements:
    app.processEvents()
    elements = frame.findAllElements('#results a')
countries = [e.toPlainText().strip() for e in elements]
print(countries)
