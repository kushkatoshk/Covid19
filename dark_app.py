import io
from typing import List, Optional
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
import markdown
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly import express as px
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')
# matplotlib.use("TkAgg")
matplotlib.use("Agg")
COLOR = "black"
BACKGROUND_COLOR = "#fff"


def main():
#     """Main function. Run this to run the app"""
#     st.sidebar.title("Layout and Style Experiments")
#     st.sidebar.header("Settings")
#     st.markdown(
#         """
# # Layout and Style Experiments
#
# The basic question is: Can we create a multi-column dashboard with plots, numbers and text using
# the [CSS Grid](https://gridbyexample.com/examples)?
#
# Can we do it with a nice api?
# Can have a dark theme?
# """
#     )

    select_block_container_style()
    # add_resources_section()

    with open(r"C:\Users\Ankush Lakkanna\Covid19\INDIA_STATES.json") as f:
        india = geojson.load(f)

    # @st.cache(persist=True)
    def load_data() :
        data = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\india_corona_data1.csv")
        return data

    st.markdown("<html style = background-color : black; color : white>", unsafe_allow_html=True)
    # COLOR = "black"
    # BACKGROUND_COLOR = "#fff"

    # state = pd.read_csv(r"C:\Users\Ankush Lakkanna\states.csv")
    df = load_data()
    last = df.shape[0]-1
    state_df = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\state_data.csv")
    pop = pd.read_csv(r"C:\Users\Ankush Lakkanna\Covid19\population.csv")
    # daily = pd.read_csv(r"C:\Users\Ankush Lakkanna\daily_corona.csv")
    dates = state_df['Date'].unique().tolist()
    latest_date = dates[-1]
    previous_date = dates[-2]
    st.title("Covid-19 India Dashboard")

    latest_data = state_df[state_df['Date']==latest_date].reset_index(drop=True)
    previous_data = state_df[state_df['Date']==previous_date].reset_index(drop=True)

    df1 = df[['Date','Active Cases']]
    df1['Date'] = pd.to_datetime(df1['Date'], format='%d-%m-%Y')
    df1.set_index('Date', inplace=True, drop=True)
    df1.index = pd.to_datetime(df1.index)

    activemodel = SARIMAX(df1, order=(0, 1, 1), seasonal_order=(0, 1, 1, 6))
    activemodel_fit = activemodel.fit(disp=False)
    activepred = []
    for i in range(1,14,2) :
        activepred.append(int(activemodel_fit.predict(len(df1)+i, len(df1)+i)))

    df2 = df[['Date','Cured / Discharged']]
    df2['Date'] = pd.to_datetime(df2['Date'], format='%d-%m-%Y')
    df2.set_index('Date', inplace=True, drop=True)
    df2.index = pd.to_datetime(df2.index)

    curedmodel = SARIMAX(df2, order=(1, 1, 1), seasonal_order=(1, 1, 1, 2))
    curedmodel_fit = curedmodel.fit(disp=False)
    curedpred = []
    for i in range(0,7) :
        curedpred.append(int(curedmodel_fit.predict(len(df2)+i, len(df2)+i)))

    df3 = df[['Date','Deaths']]
    df3['Date'] = pd.to_datetime(df3['Date'], format='%d-%m-%Y')
    df3.set_index('Date', inplace=True, drop=True)
    df3.index = pd.to_datetime(df3.index)

    deathsmodel = SARIMAX(df3, order=(1, 2, 1), seasonal_order=(1, 1, 1, 2))
    deathsmodel_fit = deathsmodel.fit(disp=False)
    deathspred = []
    for i in range(0,7) :
        deathspred.append(int(deathsmodel_fit.predict(len(df3)+i, len(df3)+i)))

    if COLOR == "black":
        template="plotly"
    else:
        template ="plotly_dark"

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

        tot = activepred[-1]+curedpred[-1]+deathspred[-1]
        total2 = (tot/spop)*1000000
        active2 = (activepred[-1]/spop)*1000000
        cured2 = (curedpred[-1]/spop)*1000000
        deaths2 = (deathspred[-1]/spop)*1000000
        mortality2 = (deathspred[-1]/tot)*100
        rate2 = (((tot - df.at[last,'Total Cases'])/ df.at[last,'Total Cases'])*100)/7
        increase2 = activepred[-1]-activepred[-2]
        recovery2 = (curedpred[-1]/(tot))*100

        st.sidebar.title("Current Numbers")
        st.sidebar.markdown("Confirmed : "+str(df.at[last, 'Total Cases']))
        st.sidebar.markdown("Active\t: "+str(df.at[last, 'Active Cases']))
        st.sidebar.markdown("Cured \t: "+str(df.at[last, 'Cured / Discharged']))
        st.sidebar.markdown("Deaths\t: "+str(df.at[last, 'Deaths']))
        st.sidebar.markdown("Increase\t: "+str(increase))
        # dark_theme = st.sidebar.checkbox("Dark Theme?", False)
        # if dark_theme:
        #     BACKGROUND_COLOR = "rgb(17,17,17)"
        #     COLOR = "#fff"
        # else :
        #     COLOR = "black"
        #     BACKGROUND_COLOR = "#fff"
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
        for i in range(1,8) :
            dot = str(datetime.today() + timedelta(days=i))[:10]
            dot = dot[8:]+'-'+dot[5:7]+'-'+dot[:4]
            datex.append(dot)
        dd = pd.DataFrame()
        dd['Date'] = datex

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
                txt3 = '3. Cured Cases : '+str(curedpred[-1])
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
        dd['Date'] = pd.to_datetime(dd['Date'], format='%d-%m-%Y')

        datelist = df['Date'].tolist()+[dd.at[0,'Date']]
        activelist = df['Active Cases'].tolist()+[activepred[0]]
        curedlist = df['Cured / Discharged'].tolist()+[curedpred[0]]
        deathslist = df['Deaths'].tolist()+[deathspred[0]]

        fig1 = go.Figure()
        fig1.update_layout(title_text = 'Active Cases with Forecast')
        fig1.add_trace(
            go.Scatter(x=datelist, y=activelist,line=dict(color='firebrick', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig1.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Active'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
        fig1.add_trace(
            go.Scatter(x=dd['Date'], y=activepred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        st.write(fig1)

        fig2 = go.Figure()
        fig2.update_layout(title_text = 'Cured Cases with Forecast')
        fig2.add_trace(
            go.Scatter(x=datelist, y=curedlist,line=dict(color='royalblue', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig2.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Cured'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
        fig2.add_trace(
            go.Scatter(x=dd['Date'], y=curedpred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig2.update_layout(hovermode="x unified")
        st.write(fig2)

        fig3 = go.Figure()
        fig3.update_layout(title_text = 'Deaths with Forecast')
        fig3.add_trace(
            go.Scatter(x=datelist, y=deathslist,line=dict(color='#575965', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig3.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Deaths'],line=dict(color='royalblue', width=2), mode='markers', name='Important Dates'))
        fig3.add_trace(
            go.Scatter(x=dd['Date'], y=deathspred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
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
        sactivepred = []
        for i in range(0,7) :
            sactivepred.append(int(sactivemodel_fit.predict(len(sdf1)+i, len(sdf1)+i)))

        sdf2 = selected_df[['Date','Cured']]
        sdf2['Date'] = pd.to_datetime(sdf2['Date'], format='%d-%m-%Y')
        sdf2.set_index('Date', inplace=True, drop=True)
        sdf2.index = pd.to_datetime(sdf2.index)

        scuredmodel = SARIMAX(sdf2, order=(1, 1, 1), seasonal_order=(1, 1, 1, 2))
        scuredmodel_fit = scuredmodel.fit(disp=False)
        scuredpred = []
        for i in range(0,7) :
            scuredpred.append(int(scuredmodel_fit.predict(len(sdf2)+i, len(sdf2)+i)))

        sdf3 = selected_df[['Date','Deaths']]
        sdf3['Date'] = pd.to_datetime(sdf3['Date'], format='%d-%m-%Y')
        sdf3.set_index('Date', inplace=True, drop=True)
        sdf3.index = pd.to_datetime(sdf3.index)

        sdeathsmodel = SARIMAX(sdf3, order=(1, 2, 1), seasonal_order=(1, 1, 1, 2), initialization='approximate_diffuse')
        sdeathsmodel_fit = sdeathsmodel.fit(disp=False)
        sdeathspred = []
        for i in range(0,7) :
            sdeathspred.append(int(sdeathsmodel_fit.predict(len(sdf3)+i, len(sdf3)+i)))

        datex = []
        for i in range(0,7) :
            dot = str(datetime.today() + timedelta(days=i))[:10]
            dot = dot[8:]+'-'+dot[5:7]+'-'+dot[:4]
            datex.append(dot)
        dd = pd.DataFrame()
        dd['Date'] = datex

        tot = activepred[-1]+curedpred[-1]+deathspred[-1]
        total2 = (tot/spop)*1000000
        active2 = (activepred[-1]/spop)*1000000
        cured2 = (curedpred[-1]/spop)*1000000
        deaths2 = (deathspred[-1]/spop)*1000000
        mortality2 = (deathspred[-1]/tot)*100
        rate2 = (((tot - df.at[last,'Total Cases'])/ df.at[last,'Total Cases'])*100)/7
        increase2 = activepred[-1]-activepred[-2]
        recovery2 = (curedpred[-1]/(tot))*100

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
                txt3 = '3. Cured Cases : '+str(curedpred[-1])
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
        dd['Date'] = pd.to_datetime(dd['Date'], format='%d-%m-%Y')

        datelist = selected_df['Date'].tolist()+[dd.at[0,'Date']]
        activelist = selected_df['Active'].astype('int64', copy=False).tolist()+[sactivepred[0]]
        curedlist = selected_df['Cured'].tolist()+[scuredpred[0]]
        deathslist = selected_df['Deaths'].tolist()+[sdeathspred[0]]

        fig1 = go.Figure()
        fig1.update_layout(title_text = 'Active Cases')
        fig1.add_trace(
            go.Scatter(x=datelist, y=activelist,line=dict(color='firebrick', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig1.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Active'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
        fig1.add_trace(
            go.Scatter(x=dd['Date'], y=sactivepred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        st.write(fig1)

        fig2 = go.Figure()
        fig2.update_layout(title_text = 'Cured Cases')
        fig2.add_trace(
            go.Scatter(x=datelist, y=curedlist,line=dict(color='royalblue', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig2.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Cured'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
        fig2.add_trace(
            go.Scatter(x=dd['Date'], y=scuredpred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        st.write(fig2)

        fig3 = go.Figure()
        fig3.update_layout(title_text = 'Deaths')
        fig3.add_trace(
            go.Scatter(x=datelist, y=deathslist,line=dict(color='#575965', width=2), mode='lines', name='Recorded', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
        fig3.add_trace(
            go.Scatter(x=dfx['Date'], y=dfx['Deaths'],line=dict(color='#575965', width=2), mode='markers', name='Important Dates'))
        fig3.add_trace(
            go.Scatter(x=dd['Date'], y=sdeathspred,line=dict(color='#EACB48', width=2), mode='lines', name='Forecast', hovertemplate ='<b>Date</b> : %{x}'+
                                                                                                                                '<br><b>Active</b> : %{y:.0}'))
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


def add_resources_section():
    """Adds a resources section to the sidebar"""
    st.sidebar.header("Add_resources_section")
    st.sidebar.markdown(
        """
- [gridbyexample.com] (https://gridbyexample.com/examples/)
"""
    )


class Cell:
    """A Cell can hold text, markdown, plots etc."""

    def __init__(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        self.class_ = class_
        self.grid_column_start = grid_column_start
        self.grid_column_end = grid_column_end
        self.grid_row_start = grid_row_start
        self.grid_row_end = grid_row_end
        self.inner_html = ""

    def _to_style(self) -> str:
        return f"""
.{self.class_} {{
    grid-column-start: {self.grid_column_start};
    grid-column-end: {self.grid_column_end};
    grid-row-start: {self.grid_row_start};
    grid-row-end: {self.grid_row_end};
}}
"""

    def text(self, text: str = ""):
        self.inner_html = text

    def markdown(self, text):
        self.inner_html = markdown.markdown(text)

    def dataframe(self, dataframe: pd.DataFrame):
        self.inner_html = dataframe.to_html()

    def plotly_chart(self, fig):
        self.inner_html = f"""
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<body>
    <p>This should have been a plotly plot.
    But since *script* tags are removed when inserting MarkDown/ HTML i cannot get it to workto work.
    But I could potentially save to svg and insert that.</p>
    <div id='divPlotly'></div>
    <script>
        var plotly_data = {fig.to_json()}
        Plotly.react('divPlotly', plotly_data.data, plotly_data.layout);
    </script>
</body>
"""

    def pyplot(self, fig=None, **kwargs):
        string_io = io.StringIO()
        plt.savefig(string_io, format="svg", fig=(2, 2))
        svg = string_io.getvalue()[215:]
        plt.close(fig)
        self.inner_html = '<div height="200px">' + svg + "</div>"

    def _to_html(self):
        return f"""<div class="box {self.class_}">{self.inner_html}</div>"""


class Grid:
    """A (CSS) Grid"""

    def __init__(
        self,
        template_columns="1 1 1",
        gap="10px",
        background_color=COLOR,
        color=BACKGROUND_COLOR,
    ):
        self.template_columns = template_columns
        self.gap = gap
        self.background_color = background_color
        self.color = color
        self.cells: List[Cell] = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        st.markdown(self._get_grid_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_html(), unsafe_allow_html=True)

    def _get_grid_style(self):
        return f"""
<style>
    .wrapper {{
    display: grid;
    grid-template-columns: {self.template_columns};
    grid-gap: {self.gap};
    background-color: {self.background_color};
    color: {self.color};
    }}
    .box {{
    background-color: {self.color};
    color: {self.background_color};
    border-radius: 5px;
    padding: 20px;
    font-size: 150%;
    }}
    table {{
        color: {self.color}
    }}
</style>
"""

    def _get_cells_style(self):
        return (
            "<style>"
            + "\n".join([cell._to_style() for cell in self.cells])
            + "</style>"
        )

    def _get_cells_html(self):
        return (
            '<div class="wrapper">'
            + "\n".join([cell._to_html() for cell in self.cells])
            + "</div>"
        )

    def cell(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        cell = Cell(
            class_=class_,
            grid_column_start=grid_column_start,
            grid_column_end=grid_column_end,
            grid_row_start=grid_row_start,
            grid_row_end=grid_row_end,
        )
        self.cells.append(cell)
        return cell


def select_block_container_style():
    """Add selection section for setting setting the max-width and padding
    of the main block container"""
    st.sidebar.header("Block Container Style")
    max_width_100_percent = st.sidebar.checkbox("Max-width: 100%?", False)
    if not max_width_100_percent:
        max_width = st.sidebar.slider("Select max-width in px", 100, 2000, 1200, 100)
    else:
        max_width = 1200
    dark_theme = st.sidebar.checkbox("Dark Theme?", False)
    padding_top = st.sidebar.number_input("Select padding top in rem", 0, 200, 5, 1)
    padding_right = st.sidebar.number_input("Select padding right in rem", 0, 200, 1, 1)
    padding_left = st.sidebar.number_input("Select padding left in rem", 0, 200, 1, 1)
    padding_bottom = st.sidebar.number_input(
        "Select padding bottom in rem", 0, 200, 10, 1
    )
    if dark_theme:
        global COLOR
        global BACKGROUND_COLOR
        BACKGROUND_COLOR = "rgb(17,17,17)"
        COLOR = "#fff"

    _set_block_container_style(
        max_width,
        max_width_100_percent,
        padding_top,
        padding_right,
        padding_left,
        padding_bottom,
    )


def _set_block_container_style(
    max_width: int = 1200,
    max_width_100_percent: bool = False,
    padding_top: int = 5,
    padding_right: int = 1,
    padding_left: int = 1,
    padding_bottom: int = 10,
):
    if max_width_100_percent:
        max_width_str = f"max-width: 100%;"
    else:
        max_width_str = f"max-width: {max_width}px;"
    st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
    .reportview-container .main {{
        color: {COLOR};
        background-color: {BACKGROUND_COLOR};
    }}
</style>
""",
        unsafe_allow_html=True,
    )


@st.cache
def get_dataframe() -> pd.DataFrame():
    """Dummy DataFrame"""
    data = [
        {"quantity": 1, "price": 2},
        {"quantity": 3, "price": 5},
        {"quantity": 4, "price": 8},
    ]
    return pd.DataFrame(data)


def get_plotly_fig():
    """Dummy Plotly Plot"""
    return px.line(data_frame=get_dataframe(), x="quantity", y="price")


def get_matplotlib_plt():
    get_dataframe().plot(kind="line", x="quantity", y="price", figsize=(5, 3))


def get_plotly_subplots():
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Table 4"),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "table"}],
        ],
    )

    fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]), row=1, col=1)

    fig.add_trace(go.Scatter(x=[20, 30, 40], y=[50, 60, 70]), row=1, col=2)

    fig.add_trace(go.Scatter(x=[300, 400, 500], y=[600, 700, 800]), row=2, col=1)

    fig.add_table(
        header=dict(values=["A Scores", "B Scores"]),
        cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]),
        row=2,
        col=2,
    )

    if COLOR == "black":
        template="plotly"
    else:
        template ="plotly_dark"
    fig.update_layout(
        height=500,
        width=700,
        title_text="Plotly Multiple Subplots with Titles",
        template=template,
    )
    return fig


main()
