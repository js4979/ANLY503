#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 17:15:53 2022

@author: jiahuiwu
"""
import pandas as pd
import os
import datetime as dt
from pycountry_convert import country_name_to_country_alpha2
import re




# read data
filenames = os.listdir("proj_data")

def read_data(path):
    return pd.read_csv(path)

files = dict()
for name in filenames:
    files[name] = read_data("proj_data/" + name)
   

    
#______________________________________
#clean

def apply_fcn(fcn):
    for name in filenames:
        fcn(name)
        # print(name)
        

#remove rows with world partner
def remove_worldPartner(filename):
    files[filename] = files[filename].loc[files[filename]["Partner"] != "World",]

apply_fcn(remove_worldPartner)


  



############
#location
#convert to standard country name
def get_country_code(country):
    try:
        code = country_name_to_country_alpha2(country)
        return code
    except:
        return "unknown"
    
def add_country_code(filename):
    files[filename]["country_code"] = files[filename]["Partner"].apply(get_country_code)
    
apply_fcn(add_country_code)

#mannually check partner with unknown country code
def country_unknown(filename):
    return list(files[filename]["Partner"].loc[files[filename]["country_code"] == "unknown"].unique())

unknown_list = []
for name in filenames:
    unknown_list.extend(country_unknown(name))
unknown_list = list(set(unknown_list))

change_dict = {}
change_dict["Bolivia (Plurinational State of)"] = "Bolivia"
change_dict["China, Hong Kong SAR"] = "Hong Kong"
change_dict["State of Palestine"] = "Palestine"
change_dict["Dem. Rep. of the Congo"] = "Congo"


def name_filter(originName):
    if originName in list(change_dict.keys()):    
        return change_dict[originName]
    return originName


def change_countryName_all(filename):
    files[filename]["Partner"] = files[filename]["Partner"].apply(name_filter)    

apply_fcn(change_countryName_all)
apply_fcn(add_country_code) #modify country code again

#check length of new unknown list
# unknown_list2 = []
# for name in filenames:
#     unknown_list2.extend(country_unknown(name))
# unknown_list2 = list(set(unknown_list2))


#delete row with unknown country code
def remove_unknown(filename):
    files[filename] = files[filename].loc[files[filename]["country_code"] != "unknown",]

apply_fcn(remove_unknown)





############
#get longitude and latitude
from geopy.geocoders import Nominatim
import numpy as np

geolocator = Nominatim(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36")

def geolocate(country):
    try:
        # Geolocate the center of the country
        loc = geolocator.geocode(country)
        # And return latitude and longitude
        return (loc.latitude, loc.longitude)
    except:
        # Return missing value
        return np.nan
    
    
#get unique country code
code_list = []
for name in filenames:
    code_list.extend(files[name]["country_code"].unique())
code_list = list(set(code_list))
    
#create location dict
loc_dict = {}
for code in code_list:
    loc_dict[code] = geolocate(code)

loc_dict
loc_dict["US"] = geolocate("US")
#set nan (GR) to location info
loc_dict["GR"] = (39.0742, 21.8243)
 
    



############
#select col


def select_col(filename):
    return files[filename][['Classification', 'Year', "Partner", 'Commodity Code', 'Commodity', 'Trade Value (US$)','country_code']]
    
temp = dict()
for name in filenames:
    temp[name] = select_col(name)


test = temp["USA_ALL_import_2020_allproduct.csv"]



def get_year(filename):
    return re.findall(r'\d+',filename)[0]

def byclass(country, filename):
    dict_ = dict()
    temp = files[filename].loc[files[filename]["Partner"] == country]
    year = get_year(filename)
    
    dict_['class'] = list(temp.groupby("Classification")["Trade Value (US$)"].sum().reset_index()["Classification"])
    dict_['sum_value'] = list(temp.groupby("Classification")["Trade Value (US$)"].sum().reset_index()["Trade Value (US$)"])
    dict_['country'] = [country] * len(dict_['sum_value'])
    dict_['coordinates'] = [list(loc_dict[country_name_to_country_alpha2(country)])] * len(dict_['sum_value'])
    dict_['datetime'] = [dt.datetime.strptime(str(year), "%Y")] * len(dict_['sum_value'])
    
    result = []
    
    for i in range(len(dict_['class'])):
        d = dict(zip(['class', 'sum_value', 'country', 'coordinates', 'datetime'], [dict_['class'][i], dict_['sum_value'][i], dict_['country'][i], dict_['coordinates'][i], dict_['datetime'][i]]))
        result.append(d)
    
    return result

def clean_file(filename):
    summary = []
    # summary['class'] = []
    # summary['sum_value'] = []
    # summary['country'] = []
    # summary['coordinates'] = []
    # summary['datetime'] = []
    for country in list(files[filename]['Partner'].unique()):
        temp = byclass(country, filename)
        summary.extend(temp)
        
        # summary['class'].extend(temp['class'])
        # summary['sum_value'].extend(temp['sum_value'])
        # summary['country'].extend(temp['country'])
        # summary['coordinates'].extend(temp['coordinates'])
        # summary['datetime'].extend(temp['datetime'])
    return summary
        

data = {}
for name in filenames:
    data[name] = clean_file(name)

    



    



        
    





    
    


    
