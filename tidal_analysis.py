"""
Tidal Analysis Script

This script contains functions for reading tidal data, processing it, and performing tidal analysis.
"""

# import modules needed here
import argparse
import os
import glob
import numpy as np
import pandas as pd
import uptide
from scipy import stats

DATA1 = "data/1947ABE.txt"

def read_tidal_data(data1):

    """Reads 1947 Aberdeen tidal data from a 
    file and returns a DataFrame."""

    # read and import data
    # ignoring header and naming columns
    data1 = pd.read_table(data1, skiprows=11,
                          names=["Cycle", "Date", "Time", "Sea Level", "Residual"], sep=r'\s+')
    # combining date and time columns
    data1["DateTime"] = pd.to_datetime(data1["Date"] + ' ' + data1["Time"])
    # dropping unnecessary columns
    data1 = data1.drop(["Cycle", "Date", "Time", "Residual"], axis = 1)
    # setting datetime as index
    data1 = data1.set_index("DateTime")
    # removing M, N, and T data
    data1.replace(to_replace=".*[MNT]$",value={'Sea Level':np.nan},regex=True,inplace=True)
    # converting sea level column from object to float
    data1["Sea Level"] = data1["Sea Level"].astype(float)

    return data1

def extract_single_year_remove_mean(year, data1):

    """Extracts a complete year from 1947 
    Aberdeen DataFrame and removes the mean."""

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

    """Extracts a given section from tidal data 
    supplied and removes the mean."""

    year1946_47 = data.loc[start:end]
    mean_sea_level = np.mean(year1946_47["Sea Level"])
    year1946_47["Sea Level"] -= mean_sea_level

    return year1946_47

def join_data(data1, data2):

    """Reads 1946 Aberdeen and 
    joins together with 1947 Aberdeen."""

    # read and format data2 through function
    data2 = read_tidal_data("data/1946ABE.txt")
    # https://saturncloud.io/blog/pandas-how-to-concatenate-dataframes-with-different-columns/
    data = pd.concat([data2, data1])

    return data

def sea_level_rise(data):

    """Calculates the linear regression of sea level 
    rise over time and returns slope and p-value."""

    filtered_data = data.dropna()
    hours = filtered_data.index.to_numpy()
    sea_level = filtered_data["Sea Level"].to_numpy()
    slope, _, _, p_value, _  = stats.linregress(hours.astype('int64' ) / 86400, sea_level)

    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):

    """Performs harmonic analysis on 
    tidal data and returns M2 and S2."""

    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    data3 = data.dropna()
    start_date = data3.index.min().strftime('%Y-%m-%d')
    end_date = data3.index.max().strftime('%Y-%m-%d').strip()
    section = extract_section_remove_mean(start_date, end_date, data3)
    tide = uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)
    seconds_since = (section.index.astype('int64').to_numpy()/1e9) - start_datetime.timestamp()
    amp,pha = uptide.harmonic_analysis(tide, section["Sea Level"].to_numpy(), seconds_since)

    return amp,pha

def get_longest_contiguous_data(data):

    """Gets the longest
    contiguous period of data."""

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

    # Used glob to find txt files in desired directory
    # https://www.delftstack.com/howto/python/read-multiple-csv-files-in-python/
    all_files = glob.glob(os.path.join(dirname, "*.txt"))

    # Read and join data files one by one to an empty dataframe
    # https://www.delftstack.com/howto/python/read-multiple-csv-files-in-python/
    all_data = pd.DataFrame()
    for filename in all_files:
        data_outer = read_tidal_data(filename)
        all_data = pd.concat([all_data, data_outer])

    # Filter out NaN values
    all_data = all_data.dropna()

    # Ensure index is DateTime
    all_data = all_data.sort_index()

    # Print station name
    print("\nStation name:" + " " + (dirname))

    # Print head and tail of tidal data
    print("\nTidal Data:")
    print(all_data)

    # Calculate and print sea level rise
    gradient, p_val = sea_level_rise(all_data)
    print("\nSea Level Rise over time (m):")
    print("Slope:", gradient)
    print("p-value:", p_val)

    # Perform and print tidal analysis
    datetime = all_data.index.min()
    amp_outer,pha_outer = tidal_analysis(all_data, ['M2', 'S2'], datetime)
    print("\nTidal Analysis (m):")
    print("M2 Amplitude:", amp_outer[0])
    print("S2 Amplitude:", amp_outer[1])
