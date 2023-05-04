#!/usr/bin/env python
# coding: utf-8

# # Mercury clustering
---
title: Solar panel installations in California 2002-2019
description: Geospatial clustering
show-code: False
params:
    map_to_show:
        input: select
        label: Chart type
        value: 'scatter_grouped'
        choices: ['scatter_grouped', 'scatter_separate_points', 'animated_heatmap']
        multi: False
    date_range:
        input: range
        label: Years to include
        value: [2002,2019]
        min: 2002
        max: 2019
    customer_segment:
        input: select
        label: Customer segment
        value: 'RES'
        choices: ['RES', 'NONRES', 'ALL']
        multi: False
    eps:
        input: slider
        label: Radius (km) to search other cluster points
        value: 5
        min: 1
        max: 7
    samples:
        input: slider
        label: Installation count required for cluster to form
        value: 1600
        min: 30
        max: 3000
    size:
        input: select
        label: Marker size
        value: 'installation_count'
        choices: ['installation_count', 'total_installed_price', 'system_size_DC', 'price_per_kW', 'average_price']
        multi: False
    color:
        input: select
        label: Marker color
        value: 'average_price'
        choices: ['installation_count', 'total_installed_price', 'system_size_DC', 'price_per_kW', 'average_price']
        multi: False
    show_amount:
        label: Max amount of clusters to show
        input: numeric
        value: 500
        min: 10
        max: 500
        step: 10
---
# In[5]:


date_range = [2002, 2019]
customer_segment = 'RES'
eps = 5
samples = 1600
size = 'installation_count' #['installation_count', 'total_installed_price', 'system_size_DC', 'price_per_kW', 'average_price']
color = 'average_price'
map_to_show = 'scatter_grouped' #['scatter_grouped', 'scatter_separate_points', 'animated_heatmap']
show_amount = 500
show_outliers = True


# In[6]:


import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint

df = pd.read_csv('data/Mercury_clustering.csv.gz') # karsittu, esikäsitelty ja pakattu versio projektin datasta
df['installation_date'] = pd.to_datetime(df['installation_date'])
df['year'] = df['installation_date'].dt.year
df['price_per_kW'] = df['total_installed_price'] / df['system_size_DC']
df['loc'] = list(zip(df['lat'], df['lon']))
df['zip_city'] = list(zip(df['city'], df['zip_code']))
date_range_ = {'start': str(date_range[0])+'-01-01', 'end': str(date_range[1])+'-12-31'}
df = df[(df['installation_date'] > date_range_['start']) & (df['installation_date'] <= date_range_['end'])]
if(customer_segment != 'ALL'): df = (df[df['customer_segment'].isin(['RES'])]) if customer_segment == 'RES' else (df[~df['customer_segment'].isin(['RES'])])

coords = df[['lat','lon']].to_numpy()
X = np.radians(coords)
earth_radius_km = 6371.0088
epsilon = eps / earth_radius_km
db = DBSCAN(eps=epsilon, min_samples=samples, algorithm='ball_tree', metric='minkowski', p=2).fit(X)

cluster_labels = db.labels_ # -1 (=ei kuulu klustereihin) tai klusterin numero
n_clusters = len(set(cluster_labels)) # määrä
cluster_arrays = pd.Series([coords[cluster_labels == n] for n in range(-1, n_clusters-1)]) # tallennetaan klusterit arrayhin 
clusters = pd.DataFrame(cluster_arrays).explode(0).rename(columns={0:'loc'}) # luodaan dataframe, jossa kukin klusteri omaksi rivikseen
clusters['cluster'] = clusters.index # tätä tarvitaan klusterin tunnistamiseen
clusters['loc'] = clusters['loc'].apply(tuple)
clusters.drop_duplicates(subset=['loc'], inplace=True)
df = pd.merge(df, clusters, on='loc') # liitetään klusteridata alkuperäiseen dataframeen

if(map_to_show != 'scatter_separate_points'):
        center_points = cluster_arrays.map(lambda x: MultiPoint(x).centroid.coords[0]) # klustereille keskipisteet
        lats, lons = zip(*center_points)
        centroids = pd.DataFrame({'lon_c':lons, 'lat_c':lats})
        centroids['cluster'] = centroids.index # tätä tarvitaan klusterin tunnistamiseen
        df = pd.merge(df, centroids) # liitetään keskipisteet alkuperäiseen dataframeen

print('Amount of clusters created:', len(df['cluster'].unique())-1)
print('Clustered installations:', len(df[df['cluster'] != 0]))
print('Not clustered installations:', len(df[df['cluster'] == 0]))
print('Total installations:', len(df))

labels = {'price_per_kW': 'Price per kW ($/kW)',
        'average_price': 'Average price ($)',
        'system_size_DC': 'Average system size (kW)', 
        'total_installed_price': "Total installed price ($)",
        'installation_count': 'Installation count',
        'cluster': 'Cluster number',
        'zip_city_size': 'Installations in single cluster point',
        'cluster_size': 'Installations in cluster'
}
if(map_to_show == 'scatter_grouped'):
        df = df.groupby('cluster').agg({'city': lambda x: list(set(x)), 'installation_date':'count', 'total_installed_price': 'sum', 'system_size_DC': 'mean', 'lat_c':'first', 'lon_c':'first'}).reset_index()
        df = df[df['cluster'] != 0]
        df = df.rename(columns={'installation_date':'installation_count'})
        df['average_price'] = (df['total_installed_price'] / df['installation_count']).round(0)
        df['price_per_kW'] = (df['total_installed_price'] / df['system_size_DC']).round(2)
        df[['system_size_DC']] = df[['system_size_DC']].round(2)
        df = df.sort_values('installation_count', ascending=0)
        if (show_amount > (len(df['cluster'].unique()))): show_amount = (len(df['cluster'].unique()))
        df = df.head(show_amount)
        df['cluster'] = df['cluster'].astype('category')
        fig = px.scatter_mapbox(df, lat=df['lat_c'], lon=df['lon_c'], hover_name='city', size=size, size_max = 30, color=color, range_color=(df[color].min(), df[color].max()), zoom=5.8, opacity=0.8,
                                mapbox_style='stamen-terrain', center = {'lat': 36.778259, 'lon': -119.417931}, labels=labels,
                                hover_data={'installation_count':True, 'average_price':True, 'system_size_DC':True, 'total_installed_price':True, 'price_per_kW':True, 'cluster':True, 'lat_c':False, 'lon_c':False}
        ) 
elif(map_to_show == 'scatter_separate_points'):
        df = df[df['cluster'] != 0]
        df['cluster_size'] = df.groupby('cluster')['cluster'].transform('count')
        df['zip_city_size'] = (df.groupby('zip_city')['zip_city'].transform('count'))
        df['cluster'] = df['cluster'].astype('category')
        df.drop_duplicates(subset=['loc'], inplace=True)
        fig = px.scatter_mapbox(df, lat=df['lat'], lon=df['lon'], hover_name='zip_city', size='zip_city_size', size_max = 20, color='cluster', zoom=5.5, opacity=0.8,
                                mapbox_style='stamen-terrain', center = {'lat': 36.778259, 'lon': -119.417931}, labels=labels,
                                hover_data={'cluster_size': True, 'cluster':True, 'lat':False, 'lon':False}
        )
elif(map_to_show == 'animated_heatmap'):
        df = df[df['cluster'] != 0]
        df = df.groupby(['year', 'cluster']).agg({'city': lambda x: list(set(x)), 'installation_date':'count', 'price_per_kW':'mean', 'total_installed_price': 'sum', 'system_size_DC': 'mean', 'lat_c':'first', 'lon_c':'first'})
        df = df.rename(columns={'installation_date':'installation_count'})
        df['average_price'] = (df['total_installed_price'] / df['installation_count']).round(0)
        df['price_per_kW'] = df['price_per_kW'].round(2)
        df = df.reset_index()
        color = 'installation_count'
        fig = px.density_mapbox(df, lat=df['lat_c'], lon=df['lon_c'], z=color, hover_name='city', zoom=5, mapbox_style='stamen-terrain', opacity=0.8,
                                animation_frame = 'year', animation_group = 'cluster', radius=40, labels=labels, center = {'lat': 36.778259, 'lon': -119.417931},
                                hover_data={'cluster':True, 'installation_count':True, 'system_size_DC':True, 'total_installed_price':True, 'price_per_kW':True, 'average_price':True, 'lat_c':False, 'lon_c':False},  
        ) 
fig.update_layout(autosize=False, 
                margin={"r":0,"t":20,"l":0,"b":0}, 
                width=1000, height=700)
fig.show()

