"""
    Author: Ojelle Rogero
    Created on: June 12, 2024
    Modified on: 
    About 
"""

from bs4 import BeautifulSoup
import requests, yaml, pytz
import datetime as dt
from dateutil import parser
import pandas as pd


class jobScrape():

    def __init__(self, time_now, hr_posted):
        self.url = "https://www.efinancialcareers.co.uk/jobs/in-United-Kingdom"
        self.min_posted = hr_posted * 60
        self.time_now = time_now


    def api_url(self, pg):
        with open("vars.yaml", "r") as f:
            vars = yaml.load(f, Loader = yaml.FullLoader)

        url, iter = "", 0
        for key, val in vars.items():
            if iter == 0: pass
            elif iter == 4: url += val + str(pg) + "&"
            else: url += val

            iter += 1
        return url


    def parser(self):
        headers = headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        content = requests.get(self.url, headers).content
        soup = BeautifulSoup(content, "html.parser")
        return soup


    def job_card(self):
        soup = self.parser()
        efc_jobcard = soup.find('efc-job-search-results').find_all('div', {'class': 'card-info'})
        return efc_jobcard
    

    def time_diff(self, posted_date):
        nw = time_now
        pdt = posted_date

        time1 = dt.datetime(nw.year, nw.month, nw.day, nw.hour, nw.minute, nw.second)
        time2 = dt.datetime(pdt.year, pdt.month, pdt.day, pdt.hour, pdt.minute, pdt.second)

        diff = time1 - time2
        mins, sec = divmod(diff.total_seconds(), 60)
        return mins
    

    def first_page(self):
        jobcard = self.job_card()

        job_title, company, job_link, location, position_type, work_arrangement, salary = [], [], [], [], [], [], []
        job_dct = {}

        for item in jobcard:
            job_title.append(item.find('h3').text)
            company.append(item.find('div', {'class': 'font-body-3'}).text.lstrip().rstrip())
            job_link.append(item.find('a').get('href'))
            location.append(item.find('span', {'class': 'dot-divider'}).text)
            position_type.append(item.find('span', {'class': 'dot-divider ng-star-inserted'}).text)

            try: work_arrangement.append(item.find('span', {'class': 'dot-divider-after ng-star-inserted'}).text)
            except: work_arrangement.append(None)

            try: salary.append(item.find('span', {'class': 'dot-divider-after last-job-criteria ng-star-inserted'}).text)
            except: salary.append(None)

        job_dct = {"Position": job_title, "Company": company, "Link": job_link, "Location": location, "Position Type": position_type,
                "Work Arrangement": work_arrangement, "Salary": salary}
        final_df = pd.DataFrame(job_dct)
        return final_df


    def next_page(self):
        job_title, company, job_link, location, position_type, work_arrangement, salary = [], [], [], [], [], [], []
        job_dct = {}
        
        diff_mins = 0
        for pg in range(1, 100):
            if diff_mins > self.min_posted: break

            pg_url = self.api_url(pg)
            data = requests.get(pg_url).json()['data']

            for i in range(0, len(data)):
                if diff_mins > self.min_posted: break
                
                posted_date = parser.parse(data[i]['postedDate'])
                diff_mins =  round(self.time_diff(posted_date) / 60, 2)

                job_title.append(data[i]['title'])
                company.append(data[i]['companyName'])
                job_link.append("https://www.efinancialcareers.co.uk" + data[i]['detailsPageUrl'])
                location.append(data[i]['jobLocation']['displayName'])

                try: position_type.append(data[i]['positionType'])
                except: position_type.append(None)
                
                try: work_arrangement.append(data[i]['workArrangementType'])
                except: work_arrangement.append(None)
                
                try: salary.append(data[i]['salary'])
                except: salary.append(None)

        job_dct = {"Position": job_title, "Company": company, "Link": job_link, "Location": location, "Position Type": position_type,
                    "Work Arrangement": work_arrangement, "Salary": salary}
        final_df = pd.DataFrame(job_dct)
        return final_df
    


    def get_data(self):
        data_1st = self.first_page()
        data_next = self.next_page()

        return data_next


if __name__ == '__main__':
    hr_posted = 2
    time_now = dt.datetime.now().astimezone(pytz.utc)

    test = jobScrape(time_now, hr_posted).get_data()

    print(test)