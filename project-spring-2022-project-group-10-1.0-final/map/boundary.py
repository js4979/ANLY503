#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 00:50:15 2022

@author: jiahuiwu
"""


import dataClean
import requests 
import json
from pycountry_convert import country_name_to_country_alpha3


url = "https://www.geoboundaries.org/gbRequest.html"



countries = []
for name in dataClean.filenames:
    countries.extend(dataClean.files[name]["Partner"].unique())
    
countries = list(set(countries))




def generate_link(country):
    return "https://www.geoboundaries.org/data/geoBoundaries-3_0_0/" + country_name_to_country_alpha3(country) + "/ADM0/geoBoundaries-3_0_0-" + country_name_to_country_alpha3(country) + "-ADM0.geojson"
    #return "https://www.geoboundaries.org/gbRequest.html?ISO=" + country_name_to_country_alpha3(country) + "&ADM=ADM0"
    # return "https://www.geoboundaries.org/api/current/gbOpen/" + country_name_to_country_alpha3(country) +  "/ADM0/"


response =requests.get(generate_link("China"))

GEO = response.json()['features'][0]["geometry"]["coordinates"]

def get_boundary(country):
    try:
        response =requests.get(generate_link(country))
    
        GEO = response.json()['features'][0]["geometry"]["coordinates"]
        # print(country)
        return GEO
    except:
        return 'error'


boundary_dict = {}
for country in countries:
    boundary_dict[country] = get_boundary(country)

# boundary_dict["United States"] = get_boundary("United States")
