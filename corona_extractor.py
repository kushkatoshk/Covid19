import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import csv
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import random
import time
import traceback
import urllib.request
import math
import datetime as dt
from datetime import datetime,timedelta


options = webdriver.ChromeOptions()

chromedriver = r"C:\Users\Ankush Lakkanna\Downloads\chromedriver_win32\chromedriver"
driver = webdriver.Chrome(r"C:\Users\Ankush Lakkanna\Downloads\chromedriver_win32\chromedriver",options=options)
os.environ["webdriver.chrome.driver"] = chromedriver
driver.get("https://www.mohfw.gov.in/")

html = driver.page_source
soup = BeautifulSoup(html,'html.parser')

div = soup.select('li.bg-blue')
div1 = soup.select('li.bg-green')
div2 = soup.select('li.bg-red')
div3 = soup.select('li.bg-orange')

cases = int(div[0].select('strong')[0].get_text())
cured = int(div1[0].select('strong')[0].get_text())
deaths = int(div2[0].select('strong')[0].get_text())
migrated = int(div3[0].select('strong')[0].get_text())

df = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\india_corona_data1.csv")

today = str(datetime.today())[:10]
yest = str(datetime.today() - timedelta(days=1))[:10]
print(today,yest)

today = today[8:]+'-'+today[5:7]+'-'+today[:4]
yest = yest[8:]+'-'+yest[5:7]+'-'+yest[:4]
# today = '03-07-2020'
# yest = '02-07-2020'
if today in df['Date'].tolist() :
    ind = df[df['Date']==today].index[0]
    df.at[ind,'Active Cases'] = cases
    df.at[ind,'Cured / Discharged'] = cured
    df.at[ind,'Deaths'] = deaths
    df.at[ind,'Migrated'] = migrated
    total = cases+cured+deaths+migrated
    df.at[ind,'Total Cases'] = total
    increase = total - df[df['Date']==yest]['Total Cases'].values[0]
    df.at[ind,'Increase in Active Cases'] = increase
else :
    df1 = pd.DataFrame(columns=['Date','Active Cases','Cured / Discharged','Deaths','Migrated'])
    df1['Date'] = [today]
    df1['Active Cases'] = [cases]
    df1['Cured / Discharged'] = [cured]
    df1['Deaths'] = [deaths]
    df1['Migrated'] = [migrated]
    total = cases+cured+deaths+migrated
    df1['Total Cases'] = [total]
    increase = total - df[df['Date']==yest]['Total Cases'].values[0]
    df1['Increase in Active Cases'] = increase
    df = df.append(df1).reset_index(drop=True)
    df = df[['Date','Active Cases','Cured / Discharged','Deaths','Migrated','Total Cases','Increase in Active Cases']]

df.to_csv(r"C:\Users\Ankush Lakkanna\Covid19\india_corona_data1.csv",index=False)

driver.close()
