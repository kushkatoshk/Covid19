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

df = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv")

today = datetime.today().strftime("%d-%m-%Y")[:10]
yest = (datetime.today() - timedelta(days=1)).strftime("%d-%m-%Y")[:10]

dates = df['Date'].unique().tolist()
if yest in dates :

	print("Already run")

else :

	options = webdriver.ChromeOptions()

	chromedriver = r"C:\Users\Ankush Lakkanna\Downloads\chromedriver_win32\chromedriver"
	driver = webdriver.Chrome(r"C:\Users\Ankush Lakkanna\Downloads\chromedriver_win32\chromedriver",options=options)
	os.environ["webdriver.chrome.driver"] = chromedriver
	driver.get("https://mohfw.gov.in/")

	html = driver.page_source
	soup = BeautifulSoup(html,'html.parser')

	print(today,yest)
	table = soup.select('table.table.table-striped')

	tr = table[0].find_all('tr')

	state = []
	scases = []
	sfn = []
	scured = []
	sdeaths = []
	for t in tr[1:-6] :
	    ele = t.find_all('td')
	    if ele[1].get_text() == 'Dadra and Nagar Haveli and Daman and Diu' :
	    	state.append('Daman and Diu')
	    else :
	    	state.append(ele[1].get_text())
	    scases.append(ele[2].get_text())
	    scured.append(ele[3].get_text())
	    sdeaths.append(ele[4].get_text())

	print(len(state))
	dfs = pd.DataFrame(columns = ['Date','State','Active','Cured','Deaths','Total'])

	dfs['State'] = state
	dfs['Active'] = scases
	dfs['Cured'] = scured
	dfs['Deaths'] = sdeaths
	dfs['Date'] = yest
	dfs['Total'] = 0

	df = df.append(dfs)
	df = df.reset_index(drop=True)

	df.to_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv",index=False)

	df = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv")

	df['Total'] = df['Active'] + df['Cured'] + df['Deaths']

	df.to_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv",index=False)

	# df = pd.read_csv(r"C:\Users\Ankush Lakkanna\india_corona_data1.csv")
	#
	# div = soup.select('li.bg-blue')
	# div1 = soup.select('li.bg-green')
	# div2 = soup.select('li.bg-red')
	# div3 = soup.select('li.bg-orange')
	#
	# cases = int(div[0].select('strong')[0].get_text())
	# cured = int(div1[0].select('strong')[0].get_text())
	# deaths = int(div2[0].select('strong')[0].get_text())
	# migrated = int(div3[0].select('strong')[0].get_text())
	#
	# total = cases+cured+deaths+migrated
	# increase = total - df[df['Date']==yest]['Total Cases'].values[0]
	# df = df.append({'Date': today, 'Active Cases': cases, 'Cured / Discharged': cured, 'Deaths': deaths, 'Migrated': migrated, 'Total Cases': total, 'Increase in Active Cases': increase}, ignore_index=True)
	# df = df[['Date','Active Cases','Cured / Discharged','Deaths','Migrated','Total Cases','Increase in Active Cases']]
	#
	#
	# df.to_csv(r"C:\Users\Ankush Lakkanna\india_corona_data1.csv",index=False)

	print("Updated")

	driver.close()
