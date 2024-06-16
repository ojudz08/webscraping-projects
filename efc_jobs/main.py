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

    def __init__(self, hr_posted):
        self.url = "https://www.efinancialcareers.co.uk/jobs/in-United-Kingdom"
        self.hr_posted = hr_posted
        self.time_now = dt.datetime.now().astimezone(pytz.utc)


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
    
        efc_jobcard = soup.find('div', {'class': 'd-flex flex-column jobs-container ng-star-inserted'}).find_all('efc-job-card')

        card_details = [card.find('efc-card-details') for card in efc_jobcard]
        card_footer = [card.find('efc-card-footer') for card in efc_jobcard]
        
        return card_details, card_footer


    def time_diff(self, time_now, posted_date):
        nw = time_now
        pdt = posted_date

        time1 = dt.datetime(nw.year, nw.month, nw.day, nw.hour, nw.minute, nw.second)
        time2 = dt.datetime(pdt.year, pdt.month, pdt.day, pdt.hour, pdt.minute, pdt.second)

        diff = time1 - time2
        mins, sec = divmod(diff.total_seconds(), 60)

        return mins

    def job_match(self, data, job):
        for i in range(0, len(data)):
            if data[i]['title'] == job:
                start_i = i
        return start_i


    def post_date(self, page, job):
        posted_mins = self.hr_posted * 60

        if page == 1:
            time_now = self.time_now
            diff_mins = 0
            job_title, posted_date = [], []

        pg_url = self.api_url(page)
        data = requests.get(pg_url).json()['data']

        start_i = self.job_match(data, job)

        for i in range(start_i, len(data)):
            if diff_mins > posted_mins: break

            posted_on = parser.parse(data[i]['postedDate'])
            diff_mins =  round(self.time_diff(time_now, posted_on), 2)
            
            posted_date.append(posted_on)
            job_title.append(data[i]['title'])
        
        return job_title, posted_date

    
    def first_page(self):
        jobcard = self.job_card()
        card_det, card_ftr = jobcard[0], jobcard[1]

        job_title, company, job_link, location, position_type, work_arrangement, salary = [], [], [], [], [], [], []
        job_dct = {}

        pg = 1
        for item in card_det:            
            # check post_date if within last_hr, match with the initial job title
            #job_tmp = # GET BACK HERE

            job_title.append(item.find('a').get('title'))
            company.append(item.find_all('div')[3].text.lstrip().rstrip())
            job_link.append(item.find('a').get('href'))
            location.append(item.find('span' , {'class': 'dot-divider'}).text)
            position_type.append(item.find('span' , {'class': 'dot-divider ng-star-inserted'}).text)
        
        for item in card_ftr:
            ln1 = len(item.find_all('div')[1])
            ln2 = len(item.find_all('div')[1].find_all('span'))
        
            if ln1 == 6 and ln2 == 2:
                work_arrangement.append(item.find_all('div')[1].find_all('span')[0].text)
                salary.append(item.find_all('div')[1].find_all('span')[1].text)
            elif (ln1 == 5 and ln2 == 1) or (ln1 == 7 and ln2 == 2):
                work_arrangement.append(None)
                salary.append(item.find_all('div')[1].find_all('span')[0].text)
        
        job_dct = {"Position": job_title, "Company": company, "Link": job_link, "Location": location, "Position Type": position_type,
                   "Work Arrangement": work_arrangement, "Salary": salary}
        final_df = pd.DataFrame(job_dct)

        return final_df
    

    def next_page(self, last_hr):
        job_title, company, job_link, location, position_type, work_arrangement, salary = [], [], [], [], [], [], []
        job_dct = {}
        
        diff_mins = 0
        for pg in range(1, 100):
            if diff_mins > last_hr: break
            pg_url = self.api_url(pg)
            data = requests.get(pg_url).json()['data']


            for i in range(0, len(data)):
                if diff_mins > last_hr: break
                
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


        return data_1st


if __name__ == '__main__':
    hr_posted = 1

    test = jobScrape(hr_posted).first_page()

    print(test)