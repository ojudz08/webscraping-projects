"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Created on: February 14, 2021
    Completed on:

    Get news articles and headline using requests, lxml and Beautifulsoup module from
         Business World: https://www.bworldonline.com/
    Update as of 2/17: Used multithreading - faster parsing
"""

from NewsParser import *

import pandas as pd
import re, os
import time
from multiprocessing.dummy import Pool as ThreadPool
import nltk


class bwOnline():

    def __init__(self, news_url, dir_output):
        self.n_url = news_url
        self.dirOut = dir_output


    def category(self):
        content = news().parse(self.n_url)
        ctgry = content.find('ul', {'id': 'menu-header-menu-1'}).find_all('a')

        #NOTE: Create a separate script for markets and health category
        markets = ['markets', 'buying rates', 'foreign interest rates', 'philippine mutual funds',
                   'leaders and laggards', 'stock quotes', 'stock markets summary',
                   'non-bsp convertible currencies', 'bsp convertible currencies', 'us commodity futures']

        ctlst = [item.text for item in ctgry if item.text != 'Health' and item.text.lower() not in markets]
        urllst = [item.get('href') for item in ctgry if item.text != 'Health' and item.text.lower() not in markets]

        lstpg = []
        for url in urllst:
            getpage = news().parse(url)
            pagetab = getpage.find('div', {'class': 'page-nav td-pb-padding-side'}).find('span', {'class': 'pages'}).text
            lstpg.append(int(re.sub(r'[^\w\s]', '', pagetab[-(len(pagetab) - 10):])))

        category = pd.DataFrame.from_dict({'Category': ctlst, 'Category Url': urllst, 'Last Page': lstpg})
        fileOutput = self.dirOut + r'\bw_category_all.csv'
        category.to_csv(fileOutput, index=False)
        return

    def article(self):
        df = pd.read_csv(self.dirOut + r'\bw_category_all.csv')
        ctgry, ctgryUrl, last = df['Category'], df['Category Url'], df['Last Page']
        top5, next10, temp10, allnews = [], [], [], []
        for i in range(0, 2):  #len(ctgry)
            top5 += self.parseTop5(ctgryUrl[i])
            pageUrl = self.generateUrl(ctgryUrl[i], 10)  #last[i]
            temp10 = self.parseMultiThread(self.parseNext10, pageUrl)
            next10 = [item for elem in temp10 for item in elem]
            allnews = top5 + next10

            artUrl = self.NewArticleUrl(allnews)
            if artUrl != []:
                artTemp = self.parseMultiThread(self.articleTitle, [ctgry[i], artUrl])
                #category, title, artUrl, pubDate = map(list, zip(*(dct.values() for dct in artTemp)))
                #article_df = pd.DataFrame.from_dict({'Category': category, 'Headlines': title, 'Article Url': artUrl,
                #                                     'Published Date': pubDate})
                #self.saveResult(article_df)
            top5, next10, temp10, allnews = [], [], [], []  # initialize back to empty list
        return artTemp #'Done parsing! Check file.'


    def parseTop5(self, url):
        ParseNewsItem = news().parse(url)
        top5 = ParseNewsItem.find('div', {'class': 'td-big-grid-wrapper'}).find_all('a', {'class': 'td-image-wrap'})
        top5Url = [item.get('href') for item in top5]
        return top5Url


    def parseNext10(self, url):
        time.sleep(1)
        ParseNewsArticle = news().parse(url)
        next10 = ParseNewsArticle.find('div', {'class': 'td-ss-main-content'}).find_all('a', {'class': 'td-image-wrap'})
        next10Url = [item.get('href') for item in next10]
        return next10Url


    def articleTitle(self, ct_url):
        category, url = ct_url[0], ct_url[1]    #artUrl, headlines, pub_date = [], [], []
        try:
            time.sleep(1)
            article = news().parseArticle(url)
            headlines = re.sub(r'[^a-zA-Z0-9]+', ' ', article.title)
            pub_date = article.publish_date
            #if headlines != '' and pub_date != '':
            return {'Category': category, 'Headlines': headlines,
                          'Article Url': url, 'Published Date': pub_date}
            #else:
            #    errUrl = pd.DataFrame.from_dict({'Category': [category], 'Article Url': [url]})
            #    self.errorUrl(errUrl)
        except Exception as errUrl:
            errUrl = pd.DataFrame.from_dict({'Category': [category], 'Article Url': [url]})
            self.errorUrl(errUrl)
            pass


    def parseMultiThread(self, func, url_li):
        pool = ThreadPool(12)
        results = pool.map(func, url_li)
        pool.close()
        pool.join()
        return results


    def generateUrl(self, url, last):
        pageUrl = [url  + f'page/{pg}/' for pg in range(1, last + 1)]
        return pageUrl


    def NewArticleUrl(self, artUrl):
        allNews = pd.read_csv(self.dirOut + r'\bw_all_news.csv')
        articleUrl = allNews['Article Url'].values.tolist()
        url = [url for url in artUrl if url not in articleUrl]
        return url


    def saveResult(self, article_df):
        allNews = pd.read_csv(self.dirOut + r'\bw_all_news.csv')
        updateNews = pd.concat([allNews, article_df], ignore_index=True)
        updateNews['Published Date'] = pd.to_datetime(updateNews['Published Date'], utc=True, format="%Y-%m-%d %H:%M:%S")
        sortedNews = updateNews.sort_values(by='Published Date', ascending=False)
        return sortedNews.to_csv(self.dirOut + r'\bw_all_news.csv', index=False)


    def errorUrl(self, errUrl):
        errFile = self.dirOut + r'\_bw_url_error.csv'
        newErr = pd.concat([pd.read_csv(errFile), errUrl])
        return newErr.to_csv(errFile, index=False)



if __name__ == "__main__":
    # Download punkt if not available
    if os.path.exists(r'C:\Users\ojell\AppData\Roaming\nltk_data\tokenizers\punkt') == False:
        nltk.download('punkt')

    print("Parsing news...")
    news_url = r'https://www.bworldonline.com/'
    dir_output = r'C:\Users\ojell\Desktop\Oj\_Thesis\Data\news\businessworld'

    bwNews = bwOnline(news_url, dir_output)

    # if os.path.exists(self.dirOut + r'\bw_category_all.csv') == False:  --> if file exist rename
    bwNews.category()     # web scrape businessworld news category

    print("Parsing with multithreading...")
    start = time.time()
    article = bwNews.article()
    print(article)
    print(len(article))
    print(f'\nW multithreading: {round(time.time() - start, 2)} sec')

    #temp = ['Top Stories', 'https://www.bworldonline.com/rates-on-hold-amid-recovery-risks/']
    #test = bwNews.articleTitle(temp)
    #print(test)