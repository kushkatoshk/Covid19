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
import os
warnings.filterwarnings('ignore')

df = pd.read_csv("india_corona_data1.csv")
last = df.shape[0]-1
state_df = pd.read_csv("state_data.csv")
pop = pd.read_csv("population.csv")
# daily = pd.read_csv(r"C:\Users\Ankush Lakkanna\daily_corona.csv")
dates = state_df['Date'].unique().tolist()
latest_date = dates[-1]
previous_date = dates[-2]

preprocess = pd.DataFrame(columns = ['State','Active','Cured','Deaths'])

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

stater = ['All States','All States','All States','All States','All States','All States','All States']

for i in range(len(activepred)) :
    preprocess = preprocess.append({'State':stater[i], 'Active':activepred[i], 'Cured':curedpred[i], 'Deaths' : deathspred[i]}, ignore_index=True)

statelist = sorted(state_df['State'].unique().tolist())

for select in statelist :

    selected_df = state_df[state_df['State']==select].reset_index(drop=True)
    last = selected_df.shape[0]-1
    increase =  selected_df.at[last,'Total'] - selected_df.at[last-1,'Total']

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

    for i in range(len(sactivepred)) :
        preprocess = preprocess.append({'State':select, 'Active':sactivepred[i], 'Cured':scuredpred[i], 'Deaths' : sdeathspred[i]}, ignore_index=True)

preprocess.to_csv('preprocess.csv', index=False)
