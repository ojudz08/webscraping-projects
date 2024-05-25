from multiprocessing.dummy import Pool as ThreadPool
import time
import requests

base_url = 'http://quotes.toscrape.com/page/'

all_urls = []

def generate_urls():
    all_urls = [base_url + str(i) for i in range(1, 51)]
    return all_urls

def scrape(url):
    res = requests.get(url)
    return res.status_code, res.url


if __name__ == '__main__':

    all_urls = generate_urls()

    start1 = time.time()
    for url in all_urls:
        print(scrape(url))
    print(f'\nElapsed: {round(time.time() - start1, 2)} sec')

    start2 = time.time()
    pool = ThreadPool(10)
    results = pool.map(scrape, all_urls)
    pool.close()
    pool.join()
    print(f'\nElapsed w multiprocessing: {round(time.time() - start2, 2)} sec')



# PLACEHOLDER
#    def saveTxt(self, article, category):
#    rawPath = self.dirOut + r'\raw'
#    file1 = open("NewsFile.txt", "w+")
#    file1.write("Title:\n")
#    file1.write(article.title)
#    file1.write("\n\nArticle Text:\n")
#    file1.write(article.text)
#    file1.write("\n\nArticle Summary:\n")
#    file1.write(article.summary)
#    file1.write("\n\n\nArticle Keywords:\n")
#    keywords = '\n'.join(article.keywords)
#    file1.write(keywords)
#    file1.close()
#    return