"""Project created on May 10, 2021
   Author: Ojelle Rogero (MSFE student - De La Salle University Manila, Philippines)
   Project Overview: Get the list of jobs and job details from efinancialcareers website 
      for Accounting Finance category and save it into a file
   """

from bs4 import BeautifulSoup
import requests
import pandas as pd


# Get the list of all job category and the corresponding url link
def byJobCat(url):
    headers = headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    cont = requests.get(url, headers).content
    soup = BeautifulSoup(cont, "html.parser")
    jobcat = soup.find("div", {"class": "job-category"}).find_all("a")
    
    jobcat_lst = []
    for category in jobcat:
        jobcat_lst.append(category.text.strip().split("\xa0")[0])
    
    category_url = []
    for link in jobcat:
        category_url.append(link.get("href"))
    
    jobcat_result = [jobcat_lst, category_url]
    
    return jobcat_result


# Get the all the job list and details
def bySector(url):
    headers = headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    cont = requests.get(url, headers).content
    soup = BeautifulSoup(cont, "html.parser")
    
    
    jobs = soup.find("ol", {"class": "jobList"}).find_all("li", {"class", "jobPreview well"})    
    job_item = []
    for job in jobs:
        job_item.append(job.find("span").text)
    
    
    jobdetails = soup.find("ol", {"class": "jobList"}).find_all("ul", {"class": "details"})
    salary = []
    location = []
    position = []
    company = []
    date = []
    for job in jobdetails:
        salary.append(job.find("li",{"class": "salary"}).text.strip())
        location.append(job.find("li",{"class": "location"}).text.strip())
        position.append(job.find("li",{"class": "position"}).text.strip())
        company.append(job.find("li",{"class": "company"}).text.strip())
        date.append(job.find("li",{"class": "updated"}).text.strip().split("\xa0\r\n                            ")[1])
      
    jobdet_result = [job_item, salary, location, position, company, date]
    
    
    return jobdet_result


main_url = "https://www.efinancialcareers.co.uk/sitemap/html#jobsBySector"
main = byJobCat(main_url)


for i in range(0, 1):
    jbct = main[0][i]
    jbct_url = main[1][i]
    
    jbdet = bySector(jbct_url)



# Compile data into dictionary and save the data into xlsx file
data = jbdet
file_path = r"C:\Users\ojell\Desktop\Oj\Projects\jobswebscrape"
file = pd.ExcelWriter(file_path + "\jobs_output.xlsx", engine="xlsxwriter")
df = pd.DataFrame(data).T
df.columns = ["Jobs", "Salary", "Location", "Tenureship", "Company", "Date Posted/Updated"]
df.to_excel(file, index=False)
file.save()




