"""
    Author: Ojelle Rogero
    Created on: June 12, 2024
    Modified on: 
    About 
"""

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


    def job_card(self):
        soup = self.parser()
        # soup.find("div", {"class": "job-category"}).find_all("a")
        efc_jobcard = soup.find("efc-job-card", {"class": "w-100 job-card ng-star-inserted"})
        card_details = efc_jobcard.find_all("efc-card-details")
        #card_footer = efc_jobcard.find_all("efc-card-footer")

        

        return card_details


if __name__ == '__main__':
    efc_url = "https://www.efinancialcareers.co.uk/jobs/in-United-Kingdom" 

    test = jobScrape(efc_url).job_card()

    for i in test:
        print(f"{i}\n")