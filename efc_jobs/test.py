from bs4 import BeautifulSoup
import requests


class jobScrape():

    def __init__(self, url):
        self.url = url
    
    def parser(self):
        headers = headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        content = requests.get(self.url, headers).content
        soup = BeautifulSoup(content, "html.parser")
        return soup
    
    def start_url(self):
        soup = self.parser()
        jobcat = soup.find("div", {"class": "job-category"}).find_all("a")
        
        jobcat_lst = []
        for category in jobcat:
            jobcat_lst.append(category.text.strip().split("\xa0")[0])
    
        category_url = []
        for link in jobcat:
            category_url.append(link.get("href"))
    
        jobcat_result = [jobcat_lst, category_url]
        return jobcat_result



if __name__ == '__main__':
    url = "https://www.efinancialcareers.co.uk/sitemap/html"

    test = jobScrape(url).start_url()
    print(test)
