"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Created on: August 13, 2021
    Completed on:

    Get news articles and headline using requests, lxml and Beautifulsoup module from
         Business World: https://www.bworldonline.com/
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from newspaper import Article
import nltk
import time

#reference: https://analyticsindiamag.com/how-to-scrape-summarize-convert-news-articles-into-text-files/

class bwOnline():

    def __init__(self, news_url, dir_output, file_output):
        self.n_url = news_url
        self.dirOut = dir_output
        self.fileOut = file_output

    def parse(self, url):
        headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        cont = requests.get(url, headers).content
        soup = BeautifulSoup(cont, 'html.parser')
        return soup

    def categoryUrl(self):
        ctgry = self.parse(self.n_url).find('ul', {'id': 'menu-header-menu-1'}).find_all('a')
        ctlst, urllst, lstpg = [], [], []
        markets = ['buying rates', 'foreign interest rates', 'philippine mutual funds',
                   'leaders and laggards', 'stock quotes', 'stock markets summary',
                   'non-bsp convertible currencies', 'bsp convertible currencies', 'us commodity futures']
        for item in ctgry:
            if item.text != 'Health' and item.text.lower() not in markets:
                ctlst.append(item.text)
                urllst.append(item.get('href'))
                temp = self.parse(item.get('href')).find('div', {'class': 'page-nav td-pb-padding-side'}).find('span', {'class': 'pages'}).text
                pg = temp[-(len(temp) - 10):]
                lstpg.append(int(re.sub(r'[^\w\s]', '', pg)))
        category = pd.DataFrame.from_dict({'Category':ctlst, 'Category Url':urllst, 'Last Page':lstpg})
        return category

    def articleUrl(self):
        ctgryUrl = self.categoryUrl()
        artUrl, tempUrl = [], []
        nltk.download('punkt')

        for i in range(1, 2): #ctgryUrl['Category Url']
            # Top 5 headlines of page 1
            cat_url = ctgryUrl['Category Url'][i]
            category = ctgryUrl['Category'][i]
            lstpg = ctgryUrl['Last Page'][i]
            top5 = self.parse(cat_url).find('div', {'class': 'td-big-grid-wrapper'}).find_all('a', {'class': 'td-image-wrap'})
            temp = [item.get('href') for item in top5]
            artUrl = artUrl + temp

            # Next 10 articles of each page
            for pg in range(1, lstpg+1): #lstpg+1
                next10 = self.parse(cat_url + f'/page/{pg}/').find('div', {'class': 'td-ss-main-content'}).find_all('a', {'class': 'td-image-wrap'})
                temp = [item.get('href') for item in next10]
                artUrl = artUrl + temp

                if pg % 10 == 0: time.sleep(5)

                # Check duplicate url and remove from list if found from master list
                if len(artUrl) >= 100 or pg == lstpg:
                    artUrl = self.removeDuplicate(artUrl)
                    if artUrl != []:
                        self.saveOutput(artUrl, pg, category)    # Pass artUrl to parase headline and saveOutput
                        artUrl = []                              # Initialize back to empty string

        if artUrl == []:
            msg = 'No new news articles'
        else:
            msg = 'Done parsing news articles!'
        return msg


    def removeDuplicate(self, artUrl):
        masterFile = pd.read_csv(self.dirOut + self.fileOut + r'.csv')
        urlColumn = masterFile['Article Url']

        urlInFile = urlColumn[urlColumn.isin(artUrl)==True].values.tolist()
        if len(urlInFile) == 0:
            return artUrl
        else:
            return [x for x in artUrl if x not in urlInFile]


    def saveOutput(self, artUrl, pg, category):
        # Parse each article
        headlines, pub_date = [], []

        for url in artUrl:
            try:
                article = Article(url, language="en")
                article.download()
                article.parse()
                article.nlp()
                headlines.append(re.sub(r'[^a-zA-Z0-9]+', ' ', article.title))
                pub_date.append(article.publish_date)
            except Exception:
                artUrl.remove(url)
                pass

        article = pd.DataFrame.from_dict({'Category': [category] * len(artUrl),
                                          'Headlines': headlines, 'Article Url': artUrl,
                                          'Published Date': pub_date})
        return article.to_csv(self.dirOut + self.fileOut + f'{pg}.csv', index=False)




if __name__ == "__main__":

    news_url = r'https://www.bworldonline.com/'
    dir_output = r'C:\Users\ojell\Desktop\Oj\_Thesis\Data\news\businessworld'
    file_output = r'\bw_corporate'

    print("Parsing news...")
    start = time.time()
    news = bwOnline(news_url, dir_output, file_output).articleUrl()
    print(news)
    #print(len(news))
    #print(type(news))

    #end = time.time()
    #elapsed = round((end - start) / 60, 2)
    #print(f'It took {elapsed} min parsing the pages')