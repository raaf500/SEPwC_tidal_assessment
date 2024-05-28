#!/usr/bin/env python3

# import the modules you need here
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import pytz
import wget
import uptide 
import math
from scipy import stats

data1 = "data/1947ABE.txt"
 
def read_tidal_data(data1):
    
    # read and import data
    # ignoring header and naming columns
    data1 = pd.read_table(data1, skiprows=11, names=["Cycle", "Date", "Time", "Sea Level", "Residual"], sep=r'\s+')
    # combining date and time columns
    data1["DateTime"] = pd.to_datetime(data1["Date"] + ' ' + data1["Time"])
    # removing unnecessary columns 
    data1 = data1.drop(["Cycle", "Date", "Time", "Residual"], axis = 1)
    # setting datetime as index
    data1 = data1.set_index("DateTime")
    # removing M, N, and T data
    data1.replace(to_replace=".*[MNT]$",value={'Sea Level':np.nan},regex=True,inplace=True)
    # converting sea level column from object to float
    data1["Sea Level"] = data1["Sea Level"].astype(float)
    
    return data1
    

def extract_single_year_remove_mean(year, data1):
    
    year = 1947
    # define start and end of datetime index
    year_string_start = str(year)+"-01-01"
    year_string_end = str(year)+"-12-31"
    # focus only on Sea level column
    year_data = data1.loc[year_string_start:year_string_end, ["Sea Level"]]
    # remove mean to oscillate around zero
    mean = np.mean(year_data["Sea Level"])
    year_data["Sea Level"] -= mean
    
    return year_data 


def extract_section_remove_mean(start, end, data):
    
    year1946_47 = data.loc[start:end]
    mean_sea_level = np.mean(year1946_47["Sea Level"])
    year1946_47["Sea Level"] -= mean_sea_level
    
    return year1946_47


def join_data(data1, data2):

    # read and format data2 through function
    data2 = read_tidal_data("data/1946ABE.txt")
    # https://saturncloud.io/blog/pandas-how-to-concatenate-dataframes-with-different-columns/
    data = pd.concat([data2, data1])
    
    return data


def sea_level_rise(data):

    filtered_data = data.dropna()

    hours = filtered_data.index.to_numpy()
    sea_level = filtered_data["Sea Level"].to_numpy()

    slope, intercept, r_value, p_value, std_err = stats.linregress(hours.astype('int64') / 86400, sea_level)

    return slope, p_value


def tidal_analysis(data, constituents, start_datetime):

    data3 = data.dropna()
    section = extract_section_remove_mean('1946-01-15', '19470310', data3)
    
    tide = uptide.Tides(['M2', 'S2'])
    tide.set_initial_time(datetime.datetime(1946,1,15,0,0,0))
 
    seconds_since = (section.index.astype('int64').to_numpy()/1e9) - datetime.datetime(1946,1,15,0,0,0).timestamp()
    amp,pha = uptide.harmonic_analysis(tide, section["Sea Level"].to_numpy(), seconds_since)

    print("M2 =", amp[0])
    print("S2 =", pha[0])

    return amp,pha


def get_longest_contiguous_data(data):

    # No test for this so use your brain

    return 





if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose
    
    # use functions here to print decent output
    # create a loop for all files, add them one by one, sicking one to another
    # eg. add one to another, then add another to the two, 
    # then add another to the three, etc


