import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
import time
import geojson
import matplotlib.pyplot as plt
import folium
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import register_matplotlib_converters
import statsmodels.api as sm
import math
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
import datetime as dt
from datetime import datetime,timedelta
from matplotlib.backends.backend_pdf import PdfPages
import warnings
register_matplotlib_converters()

warnings.filterwarnings('ignore')

# os.chdir(r"C:\Users\Ankush Lakkanna\Covid19")
with open(r"C:\Users\Ankush Lakkanna\Covid19\INDIA_STATES.json") as f:
    india = geojson.load(f)

# @st.cache(persist=True)
def load_data() :
    data = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\india_corona_data1.csv")
    return data

st.markdown("<html style = background-color : black; color : white>", unsafe_allow_html=True)
# COLOR = "black"
# BACKGROUND_COLOR = "#fff"
select = 'All States'
# state = pd.read_csv(r"C:\Users\Ankush Lakkanna\states.csv")
df = load_data()
last = df.shape[0]-1
state_df = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv")
pop = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\population.csv")

df1 = df[['Date','Active Cases']]
df1['Date'] = pd.to_datetime(df1['Date'], format='%d-%m-%Y')
df1.set_index('Date', inplace=True, drop=True)
df1.index = pd.to_datetime(df1.index)

activemodel = SARIMAX(df1, order=(0, 1, 1), seasonal_order=(0, 1, 1, 6))
activemodel_fit = activemodel.fit(disp=False)
activepred = [df.at[last,"Active Cases"]]
for i in range(1,14,2) :
    activepred.append(int(activemodel_fit.predict(len(df1)+i, len(df1)+i)))

df2 = df[['Date','Cured / Discharged']]
df2['Date'] = pd.to_datetime(df2['Date'], format='%d-%m-%Y')
df2.set_index('Date', inplace=True, drop=True)
df2.index = pd.to_datetime(df2.index)

curedmodel = SARIMAX(df2, order=(1, 1, 1), seasonal_order=(1, 1, 1, 2))
curedmodel_fit = curedmodel.fit(disp=False)
curespred = [df.at[last,"Cured / Discharged"]]
for i in range(0,7) :
    curespred.append(int(curedmodel_fit.predict(len(df2)+i, len(df2)+i)))

df3 = df[['Date','Deaths']]
df3['Date'] = pd.to_datetime(df3['Date'], format='%d-%m-%Y')
df3.set_index('Date', inplace=True, drop=True)
df3.index = pd.to_datetime(df3.index)

deathsmodel = SARIMAX(df3, order=(1, 2, 1), seasonal_order=(1, 1, 1, 2))
deathsmodel_fit = deathsmodel.fit(disp=False)
deathspred = [df.at[last,"Deaths"]]
for i in range(0,7) :
    deathspred.append(int(deathsmodel_fit.predict(len(df3)+i, len(df3)+i)))

spop = int(pop[pop['State']==select]['Population'])
last = df.shape[0]-1
total1 = (df.at[last,'Total Cases']/spop)*1000000
active1 = (df.at[last,'Active Cases']/spop)*1000000
cured1 = (df.at[last,'Cured / Discharged']/spop)*1000000
deaths1 = (df.at[last,'Deaths']/spop)*1000000
mortality = (df.at[last,'Deaths']/df.at[last,'Total Cases'])*100
rate = (((df.at[last,'Total Cases'] - df.at[last-7,'Total Cases'])/ df.at[last-7,'Total Cases'])*100)/7
increase = df.at[last, 'Increase in Active Cases']
recovery = (df.at[last, 'Cured / Discharged']/(df.at[last, 'Active Cases']+df.at[last, 'Cured / Discharged']+df.at[last, 'Deaths']))*100

tot = activepred[-1]+curespred[-1]+deathspred[-1]
total2 = (tot/spop)*1000000
active2 = (activepred[-1]/spop)*1000000
cured2 = (curespred[-1]/spop)*1000000
deaths2 = (deathspred[-1]/spop)*1000000
mortality2 = (deathspred[-1]/tot)*100
rate2 = (((tot - df.at[last,'Total Cases'])/ df.at[last,'Total Cases'])*100)/7
increase2 = activepred[-1]-activepred[-2]
recovery2 = (curespred[-1]/(tot))*100

datex = []
for i in range(0,8) :
    datex.append(datetime(2020,7,3) + timedelta(days=i))

dfx = pd.DataFrame(columns=['Date','Active','Cured','Deaths'])
dfx['Date'] = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
idate = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
iactive = []
icured = []
ideaths = []
j=0
for i in range(len(df['Date'])) :
    if df.at[i,'Date'] in idate :
        dfx.at[j,'Active'] = df.at[i,'Active Cases']
        dfx.at[j,'Cured'] = df.at[i,'Cured / Discharged']
        dfx.at[j,'Deaths'] = df.at[i,'Deaths']
        j+=1


with PdfPages('India Report.pdf') as pdf:
    firstPage = plt.figure(figsize=(11.69,8.27))
    firstPage.clf()
    txt = 'India Report'
    txt1 = str(df.at[last,'Date'])
    txt2 = 'Covid-19 India Dashboard'
    firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=28, ha="center")
    firstPage.text(0.5,0.4,txt1, transform=firstPage.transFigure, size=24, ha="center")
    firstPage.text(0.99,0.001,txt2, transform=firstPage.transFigure, size=10, ha="center")
    pdf.savefig()
    plt.close()

    secondPage = plt.figure(figsize=(11.69,8.27))
    secondPage.clf()
    txt = 'Statistics'
    txt1 = '1. Total Confirmed Cases : '+str(df.at[last, 'Total Cases'])
    txt2 = '2. Active Cases : '+str(df.at[last, 'Active Cases'])
    txt3 = '3. Cured Cases : '+str(df.at[last, 'Cured / Discharged'])
    txt4 = '4. Deaths : '+str(df.at[last, 'Deaths'])
    txt5 = '5. Daily Increase : '+str(increase)
    txt6 = '6. Total Cases Per Million : '+str(round(total1,2))
    txt7 = '7. Active Cases Per Million : '+str(round(active1,2))
    txt8 = '8. Cured Cases Per Million : '+str(round(cured1,2))
    txt9 = '9. Deaths Per Million : '+str(round(deaths1,2))
    txt10 = '10. Mortality Rate : '+str(round(mortality,2))+'%'
    txt11 = '11. Growth Rate : '+str(round(rate,2))+'%'
    txt12 = '12. Recovery Rate : '+str(round(recovery,2))+'%'
    txt13 = 'Covid-19 India Dashboard'

    secondPage.text(0.05,0.90,txt, transform=secondPage.transFigure, size=24, ha="left")
    secondPage.text(0.05,0.85,txt1, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.80,txt2, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.75,txt3, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.70,txt4, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.65,txt5, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.60,txt6, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.55,txt7, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.50,txt8, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.45,txt9, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.40,txt10, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.35,txt11, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.05,0.30,txt12, transform=secondPage.transFigure, size=20, ha="left")
    secondPage.text(0.99,0.001,txt13, transform=secondPage.transFigure, size=10, ha="right")

    pdf.savefig()
    plt.close()

    thirdPage = plt.figure(figsize=(11.69,8.27))
    thirdPage.clf()
    txt = 'Forecasts (7 days from now)'
    txt1 = '1. Total Confirmed Cases : '+str(tot)
    txt2 = '2. Active Cases : '+str(activepred[-1])
    txt3 = '3. Cured Cases : '+str(curespred[-1])
    txt4 = '4. Deaths : '+str(deathspred[-1])
    txt5 = '5. Daily Increase : '+str(increase2)
    txt6 = '6. Total Cases Per Million : '+str(round(total2,2))
    txt7 = '7. Active Cases Per Million : '+str(round(active2,2))
    txt8 = '8. Cured Cases Per Million : '+str(round(cured2,2))
    txt9 = '9. Deaths Per Million : '+str(round(deaths2,2))
    txt10 = '10. Mortality Rate : '+str(round(mortality2,2))+'%'
    txt11 = '11. Growth Rate : '+str(round(rate2,2))+'%'
    txt12 = '12. Recovery Rate : '+str(round(recovery2,2))+'%'
    txt13 = 'Covid-19 India Dashboard'

    thirdPage.text(0.05,0.90,txt, transform=thirdPage.transFigure, size=24, ha="left")
    thirdPage.text(0.05,0.85,txt1, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.80,txt2, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.75,txt3, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.70,txt4, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.65,txt5, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.60,txt6, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.55,txt7, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.50,txt8, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.45,txt9, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.40,txt10, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.35,txt11, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.05,0.30,txt12, transform=thirdPage.transFigure, size=20, ha="left")
    thirdPage.text(0.99,0.001,txt13, transform=thirdPage.transFigure, size=10, ha="right")

    pdf.savefig()
    plt.close()

    fourthPage = plt.figure(figsize=(11.69,8.27))
    fourthPage.clf()
    txt = 'Details to note before viewing graphs'
    txt1 = '1. All graphs are from 1st March, 2020 till date'
    txt2 = '2. Any steep slope upwards is a sign that a lockdown is required'
    txt3 = '3. The points marked on the graphs are in order of important dates'
    txt4 = '4. All the data used is the Public data from the MOHFW India'
    txt5 = '5. The dates are the national lockdown dates'
    txt6 = 'Important Dates '
    txt7 = 'Lockdown 1 : 25-03-2020'
    txt8 = 'Lockdown 2 : 15-04-2020'
    txt9 = 'Lockdown 3 : 04-05-2020'
    txt10 = 'Lockdown 4 : 18-05-2020'
    txt11 = 'Unlock 1 : 01-06-2020'
    txt12 = 'Covid-19 India Dashboard'

    fourthPage.text(0.05,0.90,txt, transform=fourthPage.transFigure, size=24, ha="left")
    fourthPage.text(0.05,0.85,txt1, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.80,txt2, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.75,txt3, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.70,txt4, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.65,txt5, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.55,txt6, transform=fourthPage.transFigure, size=24, ha="left")
    fourthPage.text(0.05,0.50,txt7, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.45,txt8, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.40,txt9, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.35,txt10, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.05,0.30,txt11, transform=fourthPage.transFigure, size=20, ha="left")
    fourthPage.text(0.99,0.001,txt12, transform=fourthPage.transFigure, size=10, ha="right")

    pdf.savefig()
    plt.close()

    fig = plt.figure(figsize=(11.69,8.27))
    act = 100 * df.at[last,'Active Cases']/(df.at[last,'Active Cases']+df.at[last,'Cured / Discharged']+df.at[last,'Deaths'])
    cur = 100 * df.at[last,'Cured / Discharged']/(df.at[last,'Active Cases']+df.at[last,'Cured / Discharged']+df.at[last,'Deaths'])
    dea = 100 * df.at[last,'Deaths']/(df.at[last,'Active Cases']+df.at[last,'Cured / Discharged']+df.at[last,'Deaths'])
    labels = ['Active '+str(round(act,2))+'%','Cured '+str(round(cur,2))+'%','Deaths '+str(round(dea,2))+'%']
    values = [  df.at[last,'Active Cases'], df.at[last,'Cured / Discharged'], df.at[last,'Deaths']]
    colors = [ '#EF5939', 'royalblue', '#C4C7CE']
    plt.pie(values, radius=1, colors=colors,
           wedgeprops=dict(width=0.7), labels = labels)
    txt = 'Current State of India : '+str(df.at[last,'Active Cases']+df.at[last,'Cured / Discharged']+df.at[last,'Deaths'])+" Cases"
    txt1 = 'The Pie chart shows the distribution of cases in India'
    txt2 = 'Covid-19 India Dashboard'
    plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
    plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
    plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
    pdf.savefig()
    plt.close()

    fig = plt.figure(figsize=(11.69,8.27))
    plt.plot(df['Active Cases'],color='firebrick')
    plt.plot([24,45,64,78,92], dfx['Active'], '.', color='#575965')
    plt.xlabel('Days from 1st March')
    plt.ylabel('Active Cases')
    plt.grid(True)
    txt = 'Active Cases : '+str(df.at[last,'Active Cases'])+" Cases"
    txt1 = 'The graph shows the change in Active Cases from 1st March till date'
    txt2 = 'Covid-19 India Dashboard'
    plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
    plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
    plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
    pdf.savefig()
    plt.close()

    fig = plt.figure(figsize=(11.69,8.27))
    plt.plot(df['Cured / Discharged'],color='royalblue')
    plt.plot([24,45,64,78,92], dfx['Cured'], '.', color='#575965')
    plt.xlabel('Days from 1st March')
    plt.ylabel('Cured Cases')
    plt.grid(True)
    txt = 'Cured Cases : '+str(df.at[last,'Cured / Discharged'])+" Cases"
    txt1 = 'The graph shows the change in Cured Cases from 1st March till date'
    txt2 = 'Covid-19 India Dashboard'
    plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
    plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
    plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
    pdf.savefig()
    plt.close()

    fig = plt.figure(figsize=(11.69,8.27))
    plt.plot(df['Deaths'],color='#575965')
    plt.plot([24,45,64,78,92], dfx['Deaths'], '.', color='royalblue')
    plt.xlabel('Days from 1st March')
    plt.ylabel('Deaths')
    plt.grid(True)
    txt = 'Deaths : '+str(df.at[last,'Deaths'])+" Cases"
    txt1 = 'The graph shows the change in Deaths from 1st March till date'
    txt2 = 'Covid-19 India Dashboard'
    plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
    plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
    plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
    pdf.savefig()
    plt.close()

statelist = sorted(state_df['State'].unique().tolist())

for select in statelist :
    selected_df = state_df[state_df['State']==select].reset_index(drop=True)
    last = selected_df.shape[0]-1
    last2 = selected_df.shape[0]-2
    increase =  selected_df.at[last,'Total'] - selected_df.at[last2,'Total']
    # print('pop',int(pop[pop['State']==select]['Population']))
    spop = int(pop[pop['State']==select]['Population'])
    total1 = (selected_df.at[last,'Total']/spop)*1000000
    active1 = (selected_df.at[last,'Active']/spop)*1000000
    cured1 = (selected_df.at[last,'Cured']/spop)*1000000
    deaths1 = (selected_df.at[last,'Deaths']/spop)*1000000
    mortality = (selected_df.at[last,'Deaths']/selected_df.at[last,'Total'])*100
    rate = (((selected_df.at[last,'Total'] - selected_df.at[last-7,'Total'])/ selected_df.at[last-7,'Total'])*100)/7
    recovery = (selected_df.at[last,'Cured']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths']))*100

    sdf1 = selected_df[['Date','Active']]
    sdf1['Date'] = pd.to_datetime(sdf1['Date'], format='%d-%m-%Y')
    sdf1.set_index('Date', inplace=True, drop=True)
    sdf1.index = pd.to_datetime(sdf1.index)

    sactivemodel = SARIMAX(sdf1, order=(0, 1, 1), seasonal_order=(0, 1, 1, 10))
    sactivemodel_fit = sactivemodel.fit(disp=False)
    sactivepred = [selected_df.at[last,"Active"]]
    for i in range(0,7) :
        sactivepred.append(int(sactivemodel_fit.predict(len(sdf1)+i, len(sdf1)+i)))

    sdf2 = selected_df[['Date','Cured']]
    sdf2['Date'] = pd.to_datetime(sdf2['Date'], format='%d-%m-%Y')
    sdf2.set_index('Date', inplace=True, drop=True)
    sdf2.index = pd.to_datetime(sdf2.index)

    scuredmodel = SARIMAX(sdf2, order=(1, 1, 1), seasonal_order=(1, 1, 1, 2))
    scuredmodel_fit = scuredmodel.fit(disp=False)
    scurespred = [selected_df.at[last,"Cured"]]
    for i in range(0,7) :
        scurespred.append(int(scuredmodel_fit.predict(len(sdf2)+i, len(sdf2)+i)))

    sdf3 = selected_df[['Date','Deaths']]
    sdf3['Date'] = pd.to_datetime(sdf3['Date'], format='%d-%m-%Y')
    sdf3.set_index('Date', inplace=True, drop=True)
    sdf3.index = pd.to_datetime(sdf3.index)

    sdeathsmodel = SARIMAX(sdf3, order=(1, 2, 1), seasonal_order=(1, 1, 1, 2), initialization='approximate_diffuse')
    sdeathsmodel_fit = sdeathsmodel.fit(disp=False)
    sdeathspred = [selected_df.at[last,"Deaths"]]
    for i in range(0,7) :
        sdeathspred.append(int(sdeathsmodel_fit.predict(len(sdf3)+i, len(sdf3)+i)))

    datex = []
    for i in range(0,8) :
        datex.append(datetime(2020,7,2) + timedelta(days=i))

    tot = sactivepred[-1]+scurespred[-1]+sdeathspred[-1]
    total2 = (tot/spop)*1000000
    active2 = (sactivepred[-1]/spop)*1000000
    cured2 = (scurespred[-1]/spop)*1000000
    deaths2 = (sdeathspred[-1]/spop)*1000000
    mortality2 = (sdeathspred[-1]/tot)*100
    rate2 = (((tot - selected_df.at[last,'Total'])/ selected_df.at[last,'Total'])*100)/7
    increase2 = sactivepred[-1]-sactivepred[-2]
    recovery2 = (scurespred[-1]/(tot))*100

    dfx = pd.DataFrame(columns=['Date','Active','Cured','Deaths'])
    pos = [24,45,64,78,92]
    dfx['Date'] = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
    idate = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
    iactive = []
    icured = []
    ideaths = []
    j=0
    for i in pos :
        if selected_df.shape[0] > i :
            dfx.at[j,'Active'] = selected_df.at[i,'Active']
            dfx.at[j,'Cured'] = selected_df.at[i,'Cured']
            dfx.at[j,'Deaths'] = selected_df.at[i,'Deaths']
            j+=1

    with PdfPages(str(select)+' Report.pdf') as pdf:
        firstPage = plt.figure(figsize=(11.69,8.27))
        firstPage.clf()
        txt = str(select)+' Report'
        txt1 = str(df.at[df.shape[0]-1,'Date'])
        txt2 = 'Covid-19 India Dashboard'
        firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=28, ha="center")
        firstPage.text(0.5,0.4,txt1, transform=firstPage.transFigure, size=24, ha="center")
        firstPage.text(0.99,0.001,txt2, transform=firstPage.transFigure, size=10, ha="right")
        pdf.savefig()
        plt.close()

        secondPage = plt.figure(figsize=(11.69,8.27))
        secondPage.clf()
        txt = 'Statistics'
        txt1 = '1. Total Confirmed Cases : '+str(selected_df.at[last, 'Total'])
        txt2 = '2. Active Cases : '+str(selected_df.at[last, 'Active'])
        txt3 = '3. Cured Cases : '+str(selected_df.at[last, 'Cured'])
        txt4 = '4. Deaths : '+str(selected_df.at[last, 'Deaths'])
        txt5 = '5. Increase from yesterday : '+str(increase)
        txt6 = '6. Total Cases Per Million : '+str(round(total1,2))
        txt7 = '7. Active Cases Per Million : '+str(round(active1,2))
        txt8 = '8. Cured Cases Per Million : '+str(round(cured1,2))
        txt9 = '9. Deaths Per Million : '+str(round(deaths1,2))
        txt10 = '10. Mortality Rate : '+str(round(mortality,2))+'%'
        txt11 = '11. Growth Rate : '+str(round(rate,2))+'%'
        txt12 = '12. Recovery Rate : '+str(round(recovery,2))+'%'
        txt13 = 'Covid-19 India Dashboard'

        secondPage.text(0.05,0.90,txt, transform=secondPage.transFigure, size=24, ha="left")
        secondPage.text(0.05,0.85,txt1, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.80,txt2, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.75,txt3, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.70,txt4, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.65,txt5, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.60,txt6, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.55,txt7, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.50,txt8, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.45,txt9, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.40,txt10, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.35,txt11, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.05,0.30,txt12, transform=secondPage.transFigure, size=20, ha="left")
        secondPage.text(0.99,0.001,txt13, transform=secondPage.transFigure, size=10, ha="right")

        pdf.savefig()
        plt.close()

        thirdPage = plt.figure(figsize=(11.69,8.27))
        thirdPage.clf()
        txt = 'Forecasts (7 days from now)'
        txt1 = '1. Total Confirmed Cases : '+str(tot)
        txt2 = '2. Active Cases : '+str(sactivepred[-1])
        txt3 = '3. Cured Cases : '+str(scurespred[-1])
        txt4 = '4. Deaths : '+str(sdeathspred[-1])
        txt5 = '5. Daily Increase : '+str(increase2)
        txt6 = '6. Total Cases Per Million : '+str(round(total2,2))
        txt7 = '7. Active Cases Per Million : '+str(round(active2,2))
        txt8 = '8. Cured Cases Per Million : '+str(round(cured2,2))
        txt9 = '9. Deaths Per Million : '+str(round(deaths2,2))
        txt10 = '10. Mortality Rate : '+str(round(mortality2,2))+'%'
        txt11 = '11. Growth Rate : '+str(round(rate2,2))+'%'
        txt12 = '12. Recovery Rate : '+str(round(recovery2,2))+'%'
        txt13 = 'Covid-19 India Dashboard'

        thirdPage.text(0.05,0.90,txt, transform=thirdPage.transFigure, size=24, ha="left")
        thirdPage.text(0.05,0.85,txt1, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.80,txt2, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.75,txt3, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.70,txt4, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.65,txt5, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.60,txt6, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.55,txt7, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.50,txt8, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.45,txt9, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.40,txt10, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.35,txt11, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.05,0.30,txt12, transform=thirdPage.transFigure, size=20, ha="left")
        thirdPage.text(0.99,0.001,txt13, transform=thirdPage.transFigure, size=10, ha="right")

        pdf.savefig()
        plt.close()

        fourthPage = plt.figure(figsize=(11.69,8.27))
        fourthPage.clf()
        txt = 'Details to note before viewing graphs'
        txt1 = '1. All graphs are from 1st March, 2020 till date'
        txt2 = '2. Any steep slope upwards is a sign that a lockdown is required'
        txt3 = '2. The points marked on the graphs are in order of important dates'
        txt4 = '3. All the data used is the Public data from the MOHFW India'
        txt5 = '4. The dates are the national lockdown dates'
        txt6 = 'Important Dates '
        txt7 = 'Lockdown 1 : 25-03-2020'
        txt8 = 'Lockdown 2 : 15-04-2020'
        txt9 = 'Lockdown 3 : 04-05-2020'
        txt10 = 'Lockdown 4 : 18-05-2020'
        txt11 = 'Unlock 1 : 01-06-2020'
        txt12 = 'Covid-19 India Dashboard'

        fourthPage.text(0.05,0.90,txt, transform=fourthPage.transFigure, size=24, ha="left")
        fourthPage.text(0.05,0.85,txt1, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.80,txt2, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.75,txt3, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.70,txt4, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.65,txt5, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.55,txt6, transform=fourthPage.transFigure, size=24, ha="left")
        fourthPage.text(0.05,0.50,txt7, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.45,txt8, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.40,txt9, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.35,txt10, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.05,0.30,txt11, transform=fourthPage.transFigure, size=20, ha="left")
        fourthPage.text(0.99,0.001,txt12, transform=fourthPage.transFigure, size=10, ha="right")

        pdf.savefig()
        plt.close()

        fig = plt.figure(figsize=(11.69,8.27))
        act = 100 * selected_df.at[last,'Active']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
        cur = 100 * selected_df.at[last,'Cured']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
        dea = 100 * selected_df.at[last,'Deaths']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
        labels = ['Active '+str(round(act,2))+'%','Cured '+str(round(cur,2))+'%','Deaths '+str(round(dea,2))+'%']
        # labels = ['Deaths','Active','Cured']
        values = [selected_df.at[last,'Active'], selected_df.at[last,'Cured'],selected_df.at[last,'Deaths']]
        # colors = ['mediumseagreen','firebrick','royalblue']
        colors = ['#EF5939', 'royalblue','#C4C7CE']
        plt.pie(values, radius=1, colors=colors,
               wedgeprops=dict(width=0.7), labels = labels)
        txt = 'Current State of '+str(select)
        txt1 = 'The Pie chart shows the distribution of cases in India'
        txt2 = 'Covid-19 India Dashboard'
        plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
        plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
        plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
        pdf.savefig()
        plt.close()

        fig = plt.figure(figsize=(11.69,8.27))
        plt.plot(selected_df['Active'],color='firebrick')
        plt.plot([24,45,64,78,92], dfx['Active'], '.', color='#575965')
        plt.xlabel('Days from 1st March')
        plt.ylabel('Active Cases')
        plt.grid(True)
        txt = 'Active Cases : '+str(selected_df.at[last,'Active'])+" Cases"
        txt1 = 'The graph shows the change in Active Cases from 1st March till date'
        txt2 = 'Covid-19 India Dashboard'
        plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
        plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
        plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
        pdf.savefig()
        plt.close()

        fig = plt.figure(figsize=(11.69,8.27))
        plt.plot(selected_df['Cured'],color='royalblue')
        plt.plot([24,45,64,78,92], dfx['Cured'], '.', color='#575965')
        plt.xlabel('Days from 1st March')
        plt.ylabel('Cured Cases')
        plt.grid(True)
        txt = 'Cured Cases : '+str(selected_df.at[last,'Cured'])+" Cases"
        txt1 = 'The graph shows the change in Cured Cases from 1st March till date'
        txt2 = 'Covid-19 India Dashboard'
        plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
        plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
        plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
        pdf.savefig()
        plt.close()

        fig = plt.figure(figsize=(11.69,8.27))
        plt.plot(selected_df['Deaths'],color='#575965')
        plt.plot([24,45,64,78,92], dfx['Deaths'], '.', color='royalblue')
        plt.xlabel('Days from 1st March')
        plt.ylabel('Deaths')
        plt.grid(True)
        txt = 'Deaths: '+str(selected_df.at[last,'Deaths'])+" Cases"
        txt1 = 'The graph shows the change in Deaths from 1st March till date'
        txt2 = 'Covid-19 India Dashboard'
        plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
        plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
        plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
        pdf.savefig()
        plt.close()

print('PDFs Generated!')
