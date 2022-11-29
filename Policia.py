import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import altair as alt

import geopandas as gpd

st.title('Police Deparment Incident Report')
st.write('Los Angeles Police Department is one of dozens of cities across the country that’s \
trying to predict where crime will happen—and who those future criminals will be—\
based on past crime and arrest data. One effort, known as Operation LASER, \
which began in 2011, crunches information about past offenders over a two-year\
period, using technology developed by the shadowy data analysis firm Palantir, \
and scores individuals based on their rap sheets.')

dfPoli=pd.read_csv('Police_Department_Incident_Reports__2018_to_Present.csv')
dfPoli['Filed Online'] = dfPoli['Filed Online'].fillna(False)
dfPoli_filter = dfPoli[['Incident ID','Incident Date','Incident Time','Incident Year','Incident Day of Week','Filed Online','Incident Category','Incident Subcategory','Resolution','Latitude','Longitude', 'Police District']]
dfPoli_filter = dfPoli_filter.dropna()

#----------------------------------------------------------------------------------------------

dfPoli_mapa = dfPoli_filter.rename(columns={'Latitude':'lat','Longitude':'lon'})

#Year
x = st.sidebar.slider('Year', min_value=2018, max_value=2020, step=1)

#Online
denuncia_input = st.sidebar.radio(
    "Filed Online",
    ('Yes','No')
)

#Police district
police_district_input = st.sidebar.multiselect(
    'Police District', 
    dfPoli_mapa.groupby('Police District').count().reset_index()['Police District'].tolist()
)

#Incident
incident_input = st.sidebar.multiselect(
    'Incident Category', 
    dfPoli_mapa.groupby('Incident Category').count().reset_index()['Incident Category'].tolist()
)

#Days of the week
day_input = st.sidebar.multiselect(
    'Incident Day of Week', 
    dfPoli_mapa.groupby('Incident Day of Week').count().reset_index()['Incident Day of Week'].tolist()
)

#Resolution
res_input = st.sidebar.multiselect(
    'Resolution', 
    dfPoli_mapa.groupby('Resolution').count().reset_index()['Resolution'].tolist()
)
#--------------------------------------------------------------------------------------------
#Year
dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Incident Year'] == x]

#Days of the week
if len(day_input)>0:
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Incident Day of Week'].isin(day_input)]
    
#Online
if denuncia_input == 'Yes':
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Filed Online'] == True]
else:
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Filed Online'] == False]

#Police district
if len(police_district_input)>0:
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Police District'].isin(police_district_input)]
    
#Incident type
if len(incident_input)>0:
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Incident Category'].isin(incident_input)]
    
#Resolution
if len(res_input)>0:
    dfPoli_mapa = dfPoli_mapa[dfPoli_mapa['Resolution'].isin(res_input)]
    
#st.dataframe(dfPoli_mapa)

#----------------------------------------------------------------------------------------------

selectionYear = alt.selection(type="multi", fields=["Incident Year"])
selectionRes = alt.selection(type="single", fields=["Resolution"])
selectionCat = alt.selection(type="single", fields=["Incident Category"])

base =  alt.Chart(dfPoli_mapa).properties(width=700, height=400)

Year = alt.Chart(dfPoli_mapa).mark_bar(size=25).encode(
    y = "count(Incident ID)",
    x = "Incident Year",
    tooltip=['Incident Year','count(Incident ID)'],
    color=alt.condition(selectionYear, alt.value("#E64E60"), alt.value("#FFABB5"))
).add_selection(selectionYear).properties(height=100, width=275)

Res = alt.Chart(dfPoli_mapa).mark_bar(size = 25).encode(
    y = "count(Incident ID)",
    x = "Resolution",
    color=alt.condition(selectionRes, alt.value("#E64E60"), alt.value("#FFABB5")),
    tooltip=['Resolution','count(Incident ID)'],
    text="Resolution"
).transform_filter(selectionYear).properties(height=100, width=275).add_selection(selectionRes)

Dep = alt.Chart(dfPoli_mapa).mark_bar(size = 25).encode(
    y = "count(Incident ID)",
    x = "Police District",
    color=alt.condition(selectionRes, alt.value("#E64E60"), alt.value("#FFABB5")),
    tooltip=['Police District','count(Incident ID)'],
    text="Police District"
).transform_filter(selectionYear).properties(height=100, width=275).add_selection(selectionRes)

Incident = hist = base.mark_bar().encode(
    y = "count(Incident ID)", 
    x = "Incident Category",
    tooltip=['Incident Category','count(Incident ID)'],
    color=alt.condition(selectionCat, alt.value("#E64E60"), alt.value("#FFABB5")),
).transform_filter(selectionYear).transform_filter(selectionRes).properties(height=100, width=275).add_selection(selectionCat)

dfPoli_mapa2 = dfPoli_mapa.groupby('Incident Day of Week')['Incident ID'].count()
fig = px.pie(dfPoli_mapa2, values='Incident ID', names=dfPoli_mapa2.index, color_discrete_sequence=px.colors.sequential.RdBu)

dfPoli_mapa3 = dfPoli_mapa.groupby('Incident Category')['Incident ID'].count()
fig2 = px.pie(dfPoli_mapa3, values='Incident ID', names=dfPoli_mapa3.index, color_discrete_sequence=px.colors.sequential.RdBu)

col1, col2 = st.columns(2)

with col1:
    st.map(dfPoli_mapa)
with col2:
    st.plotly_chart(fig, use_container_width=True)
#with col3:
#    st.plotly_chart(fig2, use_container_width=True)
st.altair_chart((Year | Res) & (Incident | Dep))