from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *
import lxml.html

url = 'https://www.baidu.com'
app = QApplication([])
webview = QWebView()
loop = QEventLoop()
webview.loadFinished.connect(loop.quit)
webview.load(QUrl(url))
loop.exec_()
html = webview.page().mainFrame().toHtml()
tree = lxml.html.fromstring(html)
print(tree.cssselect('#su')[0].value)