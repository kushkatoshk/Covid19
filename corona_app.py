import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

with open(r"C:\Users\Ankush Lakkanna\INDIA_STATES.json") as f:
    india = geojson.load(f)

# @st.cache(persist=True)
def load_data() :
    data = pd.read_csv(r"C:\Users\Ankush Lakkanna\india_corona_data1.csv")
    return data

st.markdown("<html style = background-color : black; color : white>", unsafe_allow_html=True)
# COLOR = "black"
# BACKGROUND_COLOR = "#fff"

# state = pd.read_csv(r"C:\Users\Ankush Lakkanna\states.csv")
df = load_data()
last = df.shape[0]-1
state_df = pd.read_csv(r"C:\Users\Ankush Lakkanna\state_data.csv")
pop = pd.read_csv(r"C:\Users\Ankush Lakkanna\population.csv")
# daily = pd.read_csv(r"C:\Users\Ankush Lakkanna\daily_corona.csv")
dates = state_df['Date'].unique().tolist()
latest_date = dates[-1]
previous_date = dates[-2]
st.title("Covid-19 India Dashboard")

latest_data = state_df[state_df['Date']==latest_date].reset_index(drop=True)
previous_data = state_df[state_df['Date']==previous_date].reset_index(drop=True)

# st.write(pdk.Deck(
#
#     map_style="mapbox://styles/mapbox/light-v9",
#     initial_view_state={
#         "latitude": 22.5937,
#         "longitude": 78.9629,
#         "zoom": 3.5,
#         "pitch":0,
#     }))
# state = pd.read_csv(r"C:\Users\Ankush Lakkanna\states.csv")
# st1 = []
# for i in range(0,len(india.features)) :
#     st1.append(india.features[i].properties['STATE'])
#
# df1= latest_data[['State','Active']].reset_index(drop=True)
# for i in range(len(st1)) :
#     for x in range(0,len(df1['State'].tolist())) :
#         if df1.at[x,'State'] == 'Telengana' and st1[i] == 'TELANGANA' :
#             df1.at[x,'State1'] = 'TELANGANA'
#         if df1.at[x,'State'].lower() in st1[i].lower() :
#             df1.at[x,'State1'] = st1[i]

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

select = st.selectbox('State', ['All States']+sorted(state_df['State'].unique().tolist()))

if select == 'All States' :
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

    st.sidebar.title("Current Numbers")
    st.sidebar.markdown("Confirmed : "+str(df.at[last, 'Total Cases']))
    st.sidebar.markdown("Active\t: "+str(df.at[last, 'Active Cases']))
    st.sidebar.markdown("Cured \t: "+str(df.at[last, 'Cured / Discharged']))
    st.sidebar.markdown("Deaths\t: "+str(df.at[last, 'Deaths']))
    st.sidebar.markdown("Increase\t: "+str(increase))
    st.sidebar.markdown(" ")
    # dark_theme = st.sidebar.checkbox("Dark Theme?", False)
    # if dark_theme:
    #     BACKGROUND_COLOR = "rgb(17,17,17)"
    #     COLOR = "#fff"
    # else :
    #     COLOR = "black"
    #     BACKGROUND_COLOR = "#fff"

    st.sidebar.markdown(" ")
    st.sidebar.title("Important Dates ")
    st.sidebar.markdown("Lockdown 1 : 25-03-2020")
    st.sidebar.markdown("Lockdown 2 : 15-04-2020")
    st.sidebar.markdown("Lockdown 3 : 04-05-2020")
    st.sidebar.markdown("Lockdown 4 : 18-05-2020")
    st.sidebar.markdown("Unlock 1 : 01-06-2020")
    st.sidebar.markdown(" ")
    st.sidebar.markdown(
        """
- [LinkedIn] (https://www.linkedin.com/in/ankush-lakkanna/)
"""
    )
    # st.sidebar.markdown("Includes "+str(df.at[last, 'Total Cases'] - latest_data.Total.sum())+" cases to be assigned to states")

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

    if st.button('Download'):
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
            txt10 = '10. Mortality Rate : '+str(round(mortality,2))
            txt11 = '11. Growth Rate : '+str(round(rate,2))
            txt12 = '12. Recovery Rate : '+str(round(recovery,2))
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
            txt10 = '10. Mortality Rate : '+str(round(mortality2,2))
            txt11 = '11. Growth Rate : '+str(round(rate2,2))
            txt12 = '12. Recovery Rate : '+str(round(recovery2,2))
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
            txt2 = '2. The Pie Chart is of the data on '+str(df.at[last,'Date'])
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
            txt = 'Active Cases'
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
            txt = 'Cured Cases'
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
            txt = 'Deaths'
            txt1 = 'The graph shows the change in Deaths from 1st March till date'
            txt2 = 'Covid-19 India Dashboard'
            plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
            plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
            plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
            pdf.savefig()
            plt.close()

    labels = ['Deaths','Active','Cured']
    colors = ['#C4C7CE', '#EF5939', 'royalblue'] #'#264F73']
    values = [df.at[last,'Deaths'].sum(), df.at[last,'Active Cases'].sum(), df.at[last,'Cured / Discharged'].sum()]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3,marker=dict(colors=colors,))])
    # fig.update_traces(marker=dict(colors=colors))
    fig.update_layout(title_text = 'Current State in India')
    st.write(fig)

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    dfx['Date'] = pd.to_datetime(dfx['Date'], format='%d-%m-%Y')

    fig1 = go.Figure()
    fig1.update_layout(title_text = 'Active Cases with Forecast')
    fig1.add_trace(
        go.Scatter(x=df['Date'], y=df['Active Cases'],line=dict(color='firebrick', width=2), mode='lines', name='Recorded'))
    fig1.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Active'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
    fig1.add_trace(
        go.Scatter(x=datex, y=activepred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    st.write(fig1)

    fig2 = go.Figure()
    fig2.update_layout(title_text = 'Cured Cases with Forecast')
    fig2.add_trace(
        go.Scatter(x=df['Date'], y=df['Cured / Discharged'],line=dict(color='royalblue', width=2), mode='lines', name='Recorded'))
    fig2.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Cured'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
    fig2.add_trace(
        go.Scatter(x=datex, y=curespred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    fig2.update_layout(hovermode="x unified")
    st.write(fig2)

    fig3 = go.Figure()
    fig3.update_layout(title_text = 'Deaths with Forecast')
    fig3.add_trace(
        go.Scatter(x=df['Date'], y=df['Deaths'],line=dict(color='#575965', width=2), mode='lines', name='Recorded'))
    fig3.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Deaths'],line=dict(color='royalblue', width=2), mode='markers', name='Important Dates'))
    fig3.add_trace(
        go.Scatter(x=datex, y=deathspred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    st.write(fig3)

    st.markdown("<span style=font-size:16pt;>Total Cases Per Million  : </span> "+str(round(total1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Active Cases Per Million : </span> "+str(round(active1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Cured Cases Per Million  : </span> "+str(round(cured1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Deaths Per Million : </span> "+str(round(deaths1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Mortality Rate : </span> "+str(round(mortality,2))+"%", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Growth Rate : </span> "+str(round(rate,2))+"%", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Recovery Rate : </span> "+str(round(recovery,2))+"%", unsafe_allow_html=True)

    st.markdown("##   State Data ")
    state1 = latest_data.sort_values(by=['Active'],ascending=False).reset_index(drop=True)
    st.table(state1)

    st.markdown("## Helpful Videos")
    st.markdown("### Covid-19 explained")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/BtN-goy9VOY' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    # st.markdown("Simulating an epidemic : https://www.youtube.com/watch?v=gxAaO2rsdIs")
    #https://www.youtube.com/watch?v=7OLpKqTriio
    st.markdown("### Simulating an epidemic")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/7OLpKqTriio' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    #https://www.youtube.com/watch?v=P27HRClMf2U
    st.markdown("### Why Face Masks are important")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/P27HRClMf2U' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(
            """
    Data Source : [Ministry of Health and Family Welfare] (https://www.mohfw.gov.in/)
    """
        )

else :

    selected_df = state_df[state_df['State']==select].reset_index(drop=True)
    last = selected_df.shape[0]-1
    increase =  selected_df.at[last,'Total'] - selected_df.at[last-1,'Total']
    spop = int(pop[pop['State']==select]['Population'])
    total1 = (selected_df.at[last,'Total']/spop)*1000000
    active1 = (selected_df.at[last,'Active']/spop)*1000000
    cured1 = (selected_df.at[last,'Cured']/spop)*1000000
    deaths1 = (selected_df.at[last,'Deaths']/spop)*1000000
    mortality = (selected_df.at[last,'Deaths']/selected_df.at[last,'Total'])*100
    rate = (((selected_df.at[last,'Total'] - selected_df.at[last-7,'Total'])/ selected_df.at[last-7,'Total'])*100)/7
    recovery = (selected_df.at[last,'Cured']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths']))*100

    st.sidebar.title("Current Numbers")
    st.sidebar.markdown("Confirmed : "+str(selected_df.at[last,'Total']))
    st.sidebar.markdown("Active\t: "+str(selected_df.at[last,'Active']))
    st.sidebar.markdown("Cured \t: "+str(selected_df.at[last,'Cured']))
    st.sidebar.markdown("Deaths\t: "+str(selected_df.at[last,'Deaths']))
    st.sidebar.markdown("Increase\t: "+str(increase))
    st.sidebar.markdown(" ")
    st.sidebar.markdown(" ")
    st.sidebar.title("Important Dates ")
    st.sidebar.markdown("Lockdown 1 : 25-03-2020")
    st.sidebar.markdown("Lockdown 2 : 15-04-2020")
    st.sidebar.markdown("Lockdown 3 : 04-05-2020")
    st.sidebar.markdown("Lockdown 4 : 18-05-2020")
    st.sidebar.markdown("Unlock 1 : 01-06-2020")
    st.sidebar.markdown(" ")
    st.sidebar.markdown(
        """
- [LinkedIn] (https://www.linkedin.com/in/ankush-lakkanna/)
"""
    )

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

    tot = activepred[-1]+curespred[-1]+deathspred[-1]
    total2 = (tot/spop)*1000000
    active2 = (activepred[-1]/spop)*1000000
    cured2 = (curespred[-1]/spop)*1000000
    deaths2 = (deathspred[-1]/spop)*1000000
    mortality2 = (deathspred[-1]/tot)*100
    rate2 = (((tot - df.at[last,'Total Cases'])/ df.at[last,'Total Cases'])*100)/7
    increase2 = activepred[-1]-activepred[-2]
    recovery2 = (curespred[-1]/(tot))*100

    dfx = pd.DataFrame(columns=['Date','Active','Cured','Deaths'])
    dfx['Date'] = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
    idate = ['25-03-2020', '15-04-2020', '04-05-2020', '18-05-2020', '01-06-2020']
    iactive = []
    icured = []
    ideaths = []
    j=0
    for i in range(len(selected_df['Date'])) :
        if selected_df.at[i,'Date'] in idate :
            dfx.at[j,'Active'] = selected_df.at[i,'Active']
            dfx.at[j,'Cured'] = selected_df.at[i,'Cured']
            dfx.at[j,'Deaths'] = selected_df.at[i,'Deaths']
            j+=1

    if st.button('Download'):
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
            txt10 = '10. Mortality Rate : '+str(round(mortality,2))
            txt11 = '11. Growth Rate : '+str(round(rate,2))
            txt12 = '12. Recovery Rate : '+str(round(recovery,2))
            txt13 = 'Covid-19 India Dashboard'

            secondPage.text(0.03,0.90,txt, transform=secondPage.transFigure, size=24, ha="left")
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
            txt10 = '10. Mortality Rate : '+str(round(mortality2,2))
            txt11 = '11. Growth Rate : '+str(round(rate2,2))
            txt12 = '12. Recovery Rate : '+str(round(recovery2,2))
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
            txt2 = '2. The Pie Chart is of the data on '+str(df.at[last,'Date'])
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
            act = 100 * selected_df.at[last,'Active']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
            cur = 100 * selected_df.at[last,'Cured']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
            dea = 100 * selected_df.at[last,'Deaths']/(selected_df.at[last,'Active']+selected_df.at[last,'Cured']+selected_df.at[last,'Deaths'])
            labels = ['Active '+str(round(act,2))+'%','Cured '+str(round(cur,2))+'%','Deaths '+str(round(dea,2))+'%']
            labels = ['Deaths','Active','Cured']
            values = [selected_df.at[last,'Deaths'], selected_df.at[last,'Active'], selected_df.at[last,'Cured']]
            # colors = ['mediumseagreen','firebrick','royalblue']
            colors = ['#C4C7CE', '#EF5939', 'royalblue']
            plt.pie(values, radius=1, colors=colors,
                   wedgeprops=dict(width=0.7), labels = labels)
            txt = 'Current State of India'
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
            txt = 'Active Cases'
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
            txt = 'Cured Cases'
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
            txt = 'Deaths'
            txt1 = 'The graph shows the change in Deaths from 1st March till date'
            txt2 = 'Covid-19 India Dashboard'
            plt.text(0.05,0.95,txt, transform=fig.transFigure, size=24, ha="left")
            plt.text(0.99,0.001,txt2, transform=fig.transFigure, size=10, ha="right")
            plt.text(0.05,0.90,txt1, transform=fig.transFigure, size=20, ha="left")
            pdf.savefig()
            plt.close()


    labels = ['Deaths','Active','Cured']
    values = [selected_df.at[last,'Deaths'], selected_df.at[last,'Active'], selected_df.at[last,'Cured']]
    # colors = ['mediumseagreen','firebrick','royalblue']
    colors = ['#C4C7CE', '#EF5939', 'royalblue']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3,marker=dict(colors=colors,))])
    # fig.update_traces(marker=dict(colors=colors))
    fig.update_layout(title_text = 'Current State in '+select)
    st.write(fig)

    selected_df['Date'] = pd.to_datetime(selected_df['Date'], format='%d-%m-%Y')
    dfx['Date'] = pd.to_datetime(dfx['Date'], format='%d-%m-%Y')

    fig1 = go.Figure()
    fig1.update_layout(title_text = 'Active Cases')
    fig1.add_trace(
        go.Scatter(x=selected_df['Date'], y=selected_df['Active'],line=dict(color='firebrick', width=2), mode='lines', name='Recorded'))
    fig1.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Active'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
    fig1.add_trace(
        go.Scatter(x=datex, y=sactivepred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    st.write(fig1)

    fig2 = go.Figure()
    fig2.update_layout(title_text = 'Cured Cases')
    fig2.add_trace(
        go.Scatter(x=selected_df['Date'], y=selected_df['Cured'],line=dict(color='royalblue', width=2), mode='lines', name='Recorded'))
    fig2.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Cured'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
    fig2.add_trace(
        go.Scatter(x=datex, y=scurespred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    st.write(fig2)

    fig3 = go.Figure()
    fig3.update_layout(title_text = 'Deaths')
    fig3.add_trace(
        go.Scatter(x=selected_df['Date'], y=selected_df['Deaths'],line=dict(color='#575965', width=2), mode='lines', name='Recorded'))
    fig3.add_trace(
        go.Scatter(x=dfx['Date'], y=dfx['Deaths'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
    fig3.add_trace(
        go.Scatter(x=datex, y=sdeathspred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast'))
    st.write(fig3)

    st.markdown("<span style=font-size:16pt;>Total Cases Per Million  : </span> "+str(round(total1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Active Cases Per Million : </span> "+str(round(active1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Cured Cases Per Million  : </span> "+str(round(cured1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Deaths Per Million : </span> "+str(round(deaths1,2))+" Per Million", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Mortality Rate : </span> "+str(round(mortality,2))+"%", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Growth Rate : </span> "+str(round(rate,2))+"%", unsafe_allow_html=True)
    st.markdown("<span style=font-size:16pt;>Recovery Rate : </span> "+str(round(recovery,2))+"%", unsafe_allow_html=True)

    st.markdown("##   State Data ")
    state1 = latest_data.sort_values(by=['Active'],ascending=False).reset_index(drop=True)
    st.table(state1)

    st.markdown("## Helpful Videos")
    st.markdown("### Covid-19 explained")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/BtN-goy9VOY' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    # st.markdown("Simulating an epidemic : https://www.youtube.com/watch?v=gxAaO2rsdIs")
    #https://www.youtube.com/watch?v=7OLpKqTriio
    st.markdown("### Simulating an epidemic")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/7OLpKqTriio' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    #https://www.youtube.com/watch?v=P27HRClMf2U
    st.markdown("### Why Face Masks are important")
    st.markdown("<iframe width='640' height='360' src='https://www.youtube.com/embed/P27HRClMf2U' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(
            """
    Data Source : [Ministry of Health and Family Welfare] (https://www.mohfw.gov.in/)
    """
        )

    # total = df1['Active'].tolist()
    # state_names = df1['State'].tolist()
    # ind1 = total.index(min(total))
    # min_name = state_names[ind1]
    # ind2 = total.index(max(total))
    # max_name= state_names[ind2]
    # df2 = pd.DataFrame()
    # df2 = df2.append(df1[df1['State']==state])
    #
    # df2 = df2.append(df1[df1['State']==min_name])
    # df2 = df2.append(df1[df1['State']==max_name])
    # df2 = df2.reset_index(drop=True)
    #
    # fig = go.Figure(data=px.choropleth(df2, geojson = india, color = 'Active', locations='State1',
    #                     featureidkey ='properties.STATE', projection="mercator",color_continuous_scale ='Reds',scope='asia'))
    # st.write(fig)

# fig = go.Figure(data=go.choropleth(df1, geojson = india, color = 'Cases', locations='State1',featureidkey ='properties.STATE', projection="mercator",color_continuous_scale ='Reds',scope='asia'))
# st.write(fig)

# india_map = folium.Map(location=[22.5937 , 78.9629], zoom_start=4, tiles='Mapbox Bright')
#
# fig = go.Figure(data= india_map.choropleth(
#     geo_data=india,
#     data=df1,
#     columns=['State1', 'Cases'],
#     key_on='feature.properties.STATE',
#     fill_color='OrRd',
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name='Active Cases in India',
# #     threshold_scale = folium.colormap.linear
# ))
# st.write(fig)






# fig = px.choropleth(df1, geojson=india, locations='State1', color='Cases',
#                            color_continuous_scale="Reds",
#                            range_color=(df1.Cases.min(), df1.Cases.max()),
#                            scope="asia",
#                            labels={'Cases':'Active Cases'}
#                           )
# # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()

# fig = go.Figure(data= india_map.choropleth(
#     geo_data=india,
#     data=df1,
#     columns=['State1', 'Cases'],
#     key_on='feature.properties.STATE',
#     fill_color='OrRd',
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name='Active Cases in India',
# #     threshold_scale = folium.colormap.linear
# ))



# st.write(df.at[0,'Date'])
# hist = np.histogram(df['Active Cases'], bins=max(df['Active Cases']), range=(0, max(df['Active Cases'])))

# df['Date']= pd.to_datetime(df['Date'], format='%d-%m-%Y')
# fig = px.bar(df, x='Date', y='Active Cases', hover_data=['Date', 'Active Cases'], height=400)
# st.write(fig)
st.markdown("</html>", unsafe_allow_html=True)
