import sys
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
from konlpy.tag import Twitter
from collections import Counter
import pytagcloud
from PyQt4 import QtGui,QtCore
import requests
from PyQt4.QtGui import*
from PyQt4.QtCore import *



 
TARGET_URL_BEFORE_PAGE_NUM = "http://news.donga.com/search?p="
TARGET_URL_BEFORE_KEWORD = '&query='
TARGET_URL_REST = '&check_news=1&more=1&sorting=3&search_date=1&v1=&v2=&range=3'
 

class UI(QtGui.QWidget):
    
    
    def __init__(self):

        
        super(UI, self).__init__()
       

        self.lblr = QtGui.QLabel("검색어: ",self)
        self.lblr.move(10,15)
        self.contents = QtGui.QLineEdit(self)
        self.contents.move(70,10)
        self.okButton = QtGui.QPushButton("확인",self)
        self.okButton.move(250,8)
        
        self.okButton.clicked.connect(self.getkeyword)
        self.lbl2 = QtGui.QLabel(self)
        self.lbl2.setGeometry(QtCore.QRect(10, 15, 860, 670))
        
        response = requests.get('http://datalab.naver.com/keyword/realtimeList.naver?where=main')
        dom = BeautifulSoup(response.text, 'html.parser')
        result = dom.find_all('ul')
        flist = []
        for res in result:
            if res['class'][0] == 'rank_list':
                keywords = res.find_all('span')
                for key in keywords:  # 상위 20개의 실시간 검색어가 들어있다.
                    print (key.contents[0])
                    flist.append(key.contents[0])
                break
    
        fkeyword = flist[0]
        print(fkeyword)
        self.lblkword = QtGui.QLabel("           <실시간 검색어>",self)
        self.lblkword.move(860,100)

        self.klist = QtGui.QListWidget(self)
        for k in range(len(flist)):
            self.klist.addItem(flist[k])
        self.klist.setGeometry(870,125,170,370)
        self.klist.itemDoubleClicked.connect(self.showItem)
        self.contents.setText(fkeyword)
        self.getkeyword()
   

        self.setGeometry(100,50,1080,660)
        self.setWindowTitle("워드 클라우드")
        self.show()

    def showItem(self,item) :
        self.contents.setText(item.text())

    def getkeyword(self):
        keyword = self.contents.text()
        print(keyword)
        pagenum = 3
        retext = "re.txt"
        main(keyword,pagenum,retext)
        print("main끝")
        wordre ="wordresult.txt"
        wordnum = 50
        print("word시작main")
        word(retext,wordnum,wordre)
        print("word끝 main")
        self.pic()
    def paintEvent(self,event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor(Qt.green))
        qp.fillRect(68,8,154,24,QBrush(QColor(0,255,0)))
        qp.fillRect(868,123,174,374,QBrush(QColor(0,255,0)))
        qp.end()

    def pic(self):
        pixmap2 = QtGui.QPixmap('wordcloud.jpg') 
        self.lbl2.setPixmap(pixmap2)
        
def get_link_from_news_title(page_num, URL, output_file):
    for i in range(page_num):
        current_page_num = 1 + i*15
        position = URL.index('=')
        URL_with_page_num = URL[: position+1] + str(current_page_num) \
                            + URL[position+1 :]
        source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
        soup = BeautifulSoup(source_code_from_URL, 'lxml',
                             from_encoding='utf-8')
        for title in soup.find_all('p', 'tit'):
            title_link = title.select('a')
            article_URL = title_link[0]['href']
            get_text(article_URL, output_file)
 
def get_text(URL, output_file):
    source_code_from_url = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_url, 'lxml', from_encoding='utf-8')
    content_of_article = soup.select('div.article_txt')
    for item in content_of_article:
        string_item = str(item.find_all(text=True))
        output_file.write(string_item)
 
 
def main(keyword,pagenum,retext):
    keyword = keyword
    page_num = int(pagenum)
    output_file_name = retext
    target_URL = TARGET_URL_BEFORE_PAGE_NUM + TARGET_URL_BEFORE_KEWORD \
                 + quote(keyword) + TARGET_URL_REST
    output_file = open(output_file_name, 'w')
    get_link_from_news_title(page_num, target_URL, output_file)
    output_file.close()

 
 
def get_tags(text, ntags=50):
    print("tag시작")
    spliter = Twitter()
    nouns = spliter.nouns(text)
    count = Counter(nouns)
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    print("tag끋")
    return return_list
 
 
def word(retext,wordnum,wordre):
    print("word시작")
    text_file_name = retext
    noun_count = int(wordnum)
    output_file_name = wordre
    open_text_file = open(text_file_name, 'r')
    text = open_text_file.read()
    nlp = Twitter()
    nou = nlp.nouns(text)
    cou = Counter(nou)
    tags2 = cou.most_common(50)
    taglist = pytagcloud.make_tags(tags2,maxsize=100)
    pytagcloud.create_tag_image(taglist,'wordcloud.jpg',size=(900,600), fontname = 'Korean')
    tags = get_tags(text, noun_count)
    open_text_file.close()
    print("word끝")
 
 
 
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())
    

