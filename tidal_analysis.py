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

    start_date = "1946-12-15"
    end_date = "1947-03-10"
    year1946_47 = data.loc[start_date:end_date]
    mean_sea_level = np.mean(year1946_47["Sea Level"])
    year1946_47["Sea Level"] -= mean_sea_level
    
    start_segment = "1947-01-15"
    end_segment = "1947-03-10"
    data_segment = data.loc[start_segment:end_segment]
    mean_sea_level_segment = np.mean(data_segment["Sea Level"])
    data_segment["Sea Level"] -= mean_sea_level_segment

    return year1946_47, data_segment


def join_data(data1, data2):

    data2 = read_tidal_data("data/1946ABE.txt")
    # https://saturncloud.io/blog/pandas-how-to-concatenate-dataframes-with-different-columns/
    data = pd.concat([data2, data1])
    
    return data


def sea_level_rise(data):

                                                     
    return 

def tidal_analysis(data, constituents, start_datetime):


    return 

def get_longest_contiguous_data(data):


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
    


