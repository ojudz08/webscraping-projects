"""
    Author: Ojelle Rogero
    Created on: June 12, 2024
    Modified on: 
    About 
"""

import os, sys
from tkinter.filedialog import *
from bs4 import BeautifulSoup
import requests, yaml, pytz
import datetime as dt
from dateutil import parser
import pandas as pd


class jobScrape():

    def __init__(self, time_now, hr_posted):
        self.init_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
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
        nw = self.time_now
        pdt = posted_date

        time1 = dt.datetime(nw.year, nw.month, nw.day, nw.hour, nw.minute, nw.second)
        time2 = dt.datetime(pdt.year, pdt.month, pdt.day, pdt.hour, pdt.minute, pdt.second)

        diff = time1 - time2
        mins, sec = divmod(diff.total_seconds(), 60)
        return mins


    def posted_date(self, job_tmp, page):
        pg_url = self.api_url(page)
        data = requests.get(pg_url).json()['data']

        for i in range(0, len(data)):
            if job_tmp == data[i]['title']:
                posted_date = parser.parse(data[i]['postedDate'])
                continue
        
        return posted_date
    

    def first_page(self):
        jobcard = self.job_card()

        job_title, company, job_link, location, position_type, work_arrangement, salary, posted_on = [], [], [], [], [], [], [], []
        job_dct = {}

        pg, diff_mins, job_tmp = 1, 0, ""
        for item in jobcard:
            if diff_mins > self.min_posted: continue

            job_title.append(item.find('h3', {'class': 'font-subtitle-3-medium ellipsis-2-row ng-star-inserted'}).text)
            
            try: company.append(item.find('div', {'class': 'font-body-3'}).text.lstrip().rstrip())
            except: company.append(None)
            
            try: job_link.append(item.find('a').get('href'))
            except: job_link.append(None)
            
            try: location.append(item.find('span', {'class': 'dot-divider'}).text)
            except: location.append(None)
            
            try: position_type.append(item.find('span', {'class': 'dot-divider ng-star-inserted'}).text)
            except: position_type.append(None)

            try: work_arrangement.append(item.find('span', {'class': 'dot-divider-after ng-star-inserted'}).text)
            except: work_arrangement.append(None)

            try: salary.append(item.find('span', {'class': 'dot-divider-after last-job-criteria ng-star-inserted'}).text)
            except: salary.append(None)

            job_tmp = item.find('h3', {'class': 'font-subtitle-3-medium ellipsis-2-row ng-star-inserted'}).text
            pdt_tmp = self.posted_date(job_tmp, pg)
            posted_on.append(pdt_tmp)

            diff_mins = self.time_diff(pdt_tmp)

        job_dct = {"Position": job_title, "Company": company, "Link": job_link, "Location": location, "Position Type": position_type,
                   "Work Arrangement": work_arrangement, "Salary": salary, "Posted Date": posted_on}
        final_df = pd.DataFrame(job_dct)

        return final_df


    def next_page(self):
        job_title, company, job_link, location, position_type, work_arrangement, salary, posted_on = [], [], [], [], [], [], [], []
        job_dct = {}
        
        for pg in range(2, 100):
            if pg > 2 and diff_mins > self.min_posted: break
            pg_url = self.api_url(pg)
            data = requests.get(pg_url).json()['data']

            for i in range(0, len(data)):
                pdt_tmp = parser.parse(data[i]['postedDate'])
                diff_mins = self.time_diff(pdt_tmp)

                if diff_mins > self.min_posted: break

                posted_on.append(pdt_tmp)
                job_title.append(data[i]['title'])
                
                try: company.append(data[i]['companyName'])
                except: company.append(None)

                try: job_link.append("https://www.efinancialcareers.co.uk" + data[i]['detailsPageUrl'])
                except: job_link.append(None)

                try: location.append(data[i]['jobLocation']['displayName'])
                except: location.append(None)

                try: position_type.append(data[i]['positionType'])
                except: position_type.append(None)
                
                try: work_arrangement.append(data[i]['workArrangementType'])
                except: work_arrangement.append(None)
                
                try: salary.append(data[i]['salary'])
                except: salary.append(None)

        job_dct = {"Position": job_title, "Company": company, "Link": job_link, "Location": location, "Position Type": position_type,
                   "Work Arrangement": work_arrangement, "Salary": salary, "Posted Date": posted_on}
        final_df = pd.DataFrame(job_dct)
        return final_df
    


    def get_data(self):
        data_1st = self.first_page()
        
        diff_mins = self.time_diff(data_1st.iloc[-1, -1])
        if diff_mins > self.min_posted: 
            return data_1st
        else:
            data_next = self.next_page()
            result = pd.concat([data_1st, data_next]).reset_index().drop('index', axis=1)
            return result


if __name__ == '__main__':
    hr_posted = 3
    time_now = dt.datetime.now().astimezone(pytz.utc)

    data_df = jobScrape(time_now, hr_posted).get_data()
    print(data_df)

