#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 01:44:28 2022

@author: jiahuiwu
"""
from boundary import boundary_dict 
import folium
import geopandas as gpd
from folium import plugins
from shapely.geometry import Polygon, mapping
import branca.colormap as cm

USA = gpd.read_file("geoBoundaries-USA-ADM0.geojson")

def Basemap():
    map1 = map1 = folium.Map(zoom_start = 2,location=[40.7, -43.98], tiles='cartodbpositron',max_bounds=True, max_zoom = 3, min_zoom = 2)
    
    # for k,r in boundary_dict.items():
    #     if r!= 'error':
    #         for poly in r:
    #             len_limit = sorted([len(poly[0]) for poly in r], reverse = True)[0]
    #             if(len(poly[0]) >= len_limit):
                        
    #                 poly = Polygon(poly[0])
                    
    #                 sim_geo = gpd.GeoSeries(poly).simplify(tolerance = 0.1)
    #                 geo_j = sim_geo.to_json()
                    
                    
    #                 geo_j = folium.GeoJson(data=geo_j,
    #                                     style_function=lambda x: {'fillColor': '#00000000','color':'black','weight':0.5})
    #                 folium.Popup(k).add_to(geo_j)
                    
    #                 geo_j.add_to(map1)
            
    #USA
    allparts = [p.buffer(0) for p in USA["geometry"][0]]
    for r in allparts:
        sim_geo = gpd.GeoSeries(r).simplify(tolerance = 0.1)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': '#00000000','color':'gray','weight':1.5})
        folium.Popup("United States").add_to(geo_j)
        geo_j.add_to(map1)
        
        
    
    return(map1)


basemap = Basemap()
basemap.save("basemap.html")



#############________________________________
#add data

from dataClean import data, filenames
import pandas as pd


def type_color(Type):
    if Type =='import':
       return  cm.step.YlOrRd_09.to_linear().scale(0, 2250)
      
    else:
        return cm.step.YlOrRd_09.to_linear().scale(0, 1450)
    

                              
def set_color(Type,value):
    cmap = type_color(Type) 
    return(pd.Series(value).map(cmap)[0])




# def generate_feature(filename):
#     Type = filename.split('_')[2]
    
#     features = [
#         {
#             "type": "Feature",
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [point["coordinates"][1], point["coordinates"][0]] ,
#             },
#             "properties": {
#                 "time": str(point["datetime"]),
#                 'style': {'color' : ''},
#                     'icon': 'circle',
#                     'iconstyle':{
#                         'fillColor': type_color(Type),
#                         'fillOpacity': 0.8,
#                         'stroke': 'true',
#                         'radius': (point['sum_value']) ** (1/3) / 550
#                     }
#             },
#         }  for point in data[filename]
       
#     ]
    
#     return features
    

def generate_feature_new(filename):
    Type = filename.split('_')[2]
    
    feature_list = []
    for point in data[filename]:
        geo = boundary_dict[point['country']];
                
        fillcolor = set_color(Type, point["sum_value"] / 10**9)
        if(geo != 'error'):
            
            len_limit = sorted([len(poly[0]) for poly in geo], reverse = True)[0]
            for poly in geo:
                if(len(poly[0]) >= len_limit):
                    poly = Polygon(poly[0]).simplify(0.1)
                    coor = mapping(poly)['coordinates'][0]
                    coor = [[i[0], i[1]] for i in coor]
                
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coor],
                        },
                        "properties": {
                            "time": str(point["datetime"]),
                            'style': {'color' : "gray", "fillColor" : fillcolor, "fillOpacity": 1, 'weight':0.7},
                                # 'iconstyle':{
                                #     'fillColor': fillcolor,
                                #     'fillOpacity': 0.8,
                                #     'stroke': 'true',
                                # }
                            'popup':  point['country'] + ": " + str(point["sum_value"] / 10**9) + " billion"
                        },
                    }
                    feature_list.append(feature)
                
    return feature_list
    
    
points_import = []
points_export = []
for name in filenames:
    Type = name.split('_')[2]
    if(Type) == "import":
        points_import.extend(generate_feature_new(name))
    else:
        points_export.extend(generate_feature_new(name))



def drawMap(points_list, Type):
    map1 = Basemap()
    plugins.TimestampedGeoJson(points_list,
                          period = 'P1Y',
                          duration = 'P1Y',
                          transition_time = 1300,
                          auto_play = True).add_to(map1)

    cmap = type_color(Type)
    _ = cmap.add_to(map1)
    cmap.caption = "sum of trade value (in billion)"

    map1.save(Type + "2.html")
    
    
drawMap(points_import, "import")
drawMap(points_export, "export")



















    
