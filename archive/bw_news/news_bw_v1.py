"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Created on: February 14, 2021
    Completed on:

    Get news articles and headline using requests, lxml and Beautifulsoup module from
         Business World: https://www.bworldonline.com/
"""

from NewsParser import *

import pandas as pd
import re, os
import time
import nltk


class bwOnline():

    def __init__(self, news_url, dir_output):
        self.n_url = news_url
        self.dirOut = dir_output


    def category(self):
        content = news().parse(self.n_url)
        ctgry = content.find('ul', {'id': 'menu-header-menu-1'}).find_all('a')

        markets = ['buying rates', 'foreign interest rates', 'philippine mutual funds',
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
        fileName = r'\bw_category'
        self.saveResult(category, fileName, 'all')
        return


    def article(self):
        if os.path.exists(self.dirOut + r'\bw_category_all.csv') == False:
            self.category()
            return 'Done parsing category since file did not exist.'

        df = pd.read_csv(self.dirOut + r'\bw_category_all.csv')
        cat, ctgryUrl, lst = df['Category'], df['Category Url'], df['Last Page']

        for i in range(0, 1): #ctgryUrl[i]
            artUrl = []
            category = cat[i]
            url = ctgryUrl[i]
            ParseNewsItem = news().parse(url)
            top5 = ParseNewsItem.find('div', {'class': 'td-big-grid-wrapper'}).find_all('a', {'class': 'td-image-wrap'})
            artUrl = artUrl + [item.get('href') for item in top5]

            lstpg = lst[i]
            for pg in range(1, lstpg + 1):
                ParseNewsArticle = news().parse(url + f'/page/{pg}/')
                next10 = ParseNewsArticle.find('div', {'class': 'td-ss-main-content'}).find_all('a', {'class': 'td-image-wrap'})
                artUrl = artUrl + [item.get('href') for item in next10]
                if pg % 5 == 0: time.sleep(5)              # Pause 5 sec for every 10 pages

                if len(artUrl) >= 500 or pg == lstpg:
                    artUrl = self.NewArticleUrl(artUrl, category.lower())     # Get only urls of new released news article not in masterfile
                    if artUrl != []:
                        article = self.parseArticle(category, artUrl)
                        fileName = r'\bw_' + category.lower()
                        self.saveResult(article, fileName, pg)          # Save each new parsed article into a new csv
                        artUrl = []   #initialize back to empty list after saving
        return 'Done parsing updated news articles'


    def NewArticleUrl(self, artUrl, category):
        masterFile = pd.read_csv(self.dirOut + r'\bw_' + category + r'.csv')
        articlUrl = masterFile['Article Url'].values.tolist()
        url = [url for url in artUrl if url not in articlUrl]
        return url


    def parseArticle(self, category, artUrl):
        headlines, pub_date = [], []
        for url in artUrl:
            try:
                article = news().parseArticle(url)
                headlines.append(re.sub(r'[^a-zA-Z0-9]+', ' ', article.title))
                pub_date.append(article.publish_date)

                # GET BACK HERE, save as txt file all parsed data
                #self.saveTxt(article, category.lower())
            except Exception:
                errUrl = pd.DataFrame.from_dict({'Category': [category], 'Article Url': [url]})
                self.errorUrl(errUrl)
                artUrl.remove(url)
                pass
        df = pd.DataFrame.from_dict({'Category': [category] * len(artUrl),
                                     'Headlines': headlines, 'Article Url': artUrl,
                                     'Published Date': pub_date})
        return df


    def saveTxt(self, article, category):
        rawPath = self.dirOut + r'\raw'
        file1 = open("NewsFile.txt", "w+")
        file1.write("Title:\n")
        file1.write(article.title)
        file1.write("\n\nArticle Text:\n")
        file1.write(article.text)
        file1.write("\n\nArticle Summary:\n")
        file1.write(article.summary)
        file1.write("\n\n\nArticle Keywords:\n")
        keywords = '\n'.join(article.keywords)
        file1.write(keywords)
        file1.close()
        return


    def saveResult(self, df, fileName, pg):
        fileOutput = self.dirOut + fileName + f'_{pg}.csv'
        return df.to_csv(fileOutput, index=False)


    def errorUrl(self, errUrl):
        errFile = self.dirOut + r'\_bw_url_error.csv'
        newErr = pd.concat([pd.read_csv(errFile), errUrl])
        return newErr.to_csv(errFile, index=False)



if __name__ == "__main__":
    # Download punkt if not available
    if os.path.exists(r'C:\Users\ojell\AppData\Roaming\nltk_data\tokenizers\punkt') == False:
        nltk.download('punkt')

    print("Parsing news...")

    start = time.time()

    news_url = r'https://www.bworldonline.com/'
    dir_output = r'C:\Users\ojell\Desktop\Oj\_Thesis\Data\news\businessworld'

    bwNews = bwOnline(news_url, dir_output).article()
    print(bwNews)

    end = time.time()
    elapsed = round((end - start), 2)
    print(f'It took {elapsed} sec')