"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Modified version: February 14, 2021

    Main script for parsing news articles
"""

from bs4 import BeautifulSoup
import requests
from newspaper import Article

class news:

    def __init__(self):
        pass

    def parse(self, url):
        headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        cont = requests.get(url, headers).content
        soup = BeautifulSoup(cont, 'html.parser')
        return soup

    def parseArticle(self, url):
        article = Article(url, language="en")
        article.download()
        article.parse()
        article.nlp()
        return article