"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Created on: February 14, 2021
    Completed on:

    Get news articles and headline using requests, lxml and Beautifulsoup module from
         Business World: https://www.bworldonline.com/
    Update as of 2/24: Update multithreading
"""

from NewsParser import *

import pandas as pd
import re, os
import time
import threading

class bwOnline():
    def __init__(self, news_url, dir_output):
        self.ctgry = news().parse(news_url).find('ul', {'id': 'menu-header-menu-1'}).find_all('a')
        self.dirOut = dir_output
        self.markets = ['markets', 'buying rates', 'foreign interest rates', 'philippine mutual funds',
                        'leaders and laggards', 'stock quotes', 'stock markets summary',
                        'non-bsp convertible currencies', 'bsp convertible currencies', 'us commodity futures']
        self.lock = threading.Lock()

    def category(self):
        ctlst = [item.text for item in self.ctgry if item.text != 'Health' and item.text.lower() not in self.markets]
        urllst = [item.get('href') for item in self.ctgry if item.text != 'Health' and item.text.lower() not in self.markets]
        lstpg = []
        for url in urllst:
            getpage = news().parse(url)
            pagetab = getpage.find('div', {'class': 'page-nav td-pb-padding-side'}).find('span', {'class': 'pages'}).text
            lstpg.append(int(re.sub(r'[^\w\s]', '', pagetab[-(len(pagetab) - 10):])))
        return

    def cat_li(self):
        ctlst = [item.text for item in self.ctgry if item.text != 'Health' and item.text.lower() not in self.markets]
        return ctlst

    def url_li(self):
        urllst = [item.get('href') for item in self.ctgry if item.text != 'Health' and item.text.lower() not in self.markets]
        return urllst

    def lst_li(self):
        urllst = self.url_li()
        lstpg = []
        for url in urllst:
            getpage = news().parse(url)
            pagetab = getpage.find('div', {'class': 'page-nav td-pb-padding-side'}).find('span', {'class': 'pages'}).text
            lstpg.append(int(re.sub(r'[^\w\s]', '', pagetab[-(len(pagetab) - 10):])))
        return lstpg

    def category2(self):
        ctgry = threading.Thread(target=self.cat_li, args=(1,))
        #url = threading.Thread(target=self.url_li(), args=(1,))
        #lstpage = threading.Thread(target=self.lst_li(), args=(1,))

        ctgry.start()
        #url.start()
        #lstpage.start()

        #ctgry.join()
        #url.join()
        #lstpage.join()

        time.sleep(5)

        #category = pd.DataFrame.from_dict({'Category': future1.result(), 'Category Url': future2.result(),
        #                                   'Last Page': future3.result()})
        return ctgry


if __name__ == "__main__":
    news_url = r'https://www.bworldonline.com/'
    dir_output = r'C:\Users\ojell\Desktop\Oj\_Thesis\Data\news\businessworld'

    bwNews = bwOnline(news_url, dir_output)

    #print("Normal parsing news")
    #start1 = time.time()
    #category = bwNews.category1()
    #print(f'Elapsed time: {round(time.time() - start1, 2)} sec')

    print('\n')
    start2 = time.time()
    #category = bwNews.category2()

    ctgry = threading.Thread(target=bwNews.cat_li)
    ctgry.start()

    url = threading.Thread(target=bwNews.url_li)
    url.start()

    ctgry.join()
    url.join()

    category = pd.DataFrame.from_dict({'Category': ctgry[0], 'Category Url': url[0]})
    print(category)

    print(f'Elapsed time: {round(time.time() - start2, 2)} sec')
