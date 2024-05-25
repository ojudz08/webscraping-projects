"""
    Author: Ojelle Rogero
    Created on: May 10, 2021
    Modified on: September 23, 2023
    About:
        <ONGOING PROJECT...>
        Web scrape jobs and job details from efinancialcareers website 
        for Accounting Finance category and save it into a file
    Modification / Updates:
        Re-coded script and created functions
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd

class jobScrape():

    def __init__(self, url):
        self.url = url
    
    def parser(self):
        headers = headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        content = requests.get(self.url, headers).content
        soup = BeautifulSoup(content, "html.parser")

        return soup
    
    def byJobCat(self):
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

    def bySector(self):
        soup = self.parser()
        jobs = soup.find("ol", {"class": "jobList"}).find_all("li", {"class", "jobPreview well"})    
        
        job_item = []
        for job in jobs:
            job_item.append(job.find("span").text)

        jobdetails = soup.find("ol", {"class": "jobList"}).find_all("ul", {"class": "details"})
        salary, location, position, company, date = [], [], [], [], 
        for job in jobdetails:
            salary.append(job.find("li",{"class": "salary"}).text.strip())
            location.append(job.find("li",{"class": "location"}).text.strip())
            position.append(job.find("li",{"class": "position"}).text.strip())
            company.append(job.find("li",{"class": "company"}).text.strip())
            date.append(job.find("li",{"class": "updated"}).text.strip().split("\xa0\r\n                            ")[1])
      
        jobdet_result = [job_item, salary, location, position, company, date]    
        
        return jobdet_result
    

if __name__ == '__main__':
    url = "https://www.efinancialcareers.co.uk/sitemap/html#jobsBySector"

    job_scrape = jobScrape(url)
    test = job_scrape.bySector()
    print(test)

