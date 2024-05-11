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
data2 = "data/1946ABE.txt"

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
    

def extract_single_year_remove_mean(year, data):
    
    return 


def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):

    return 



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
    


