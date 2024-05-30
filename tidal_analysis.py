"""
Tidal Analysis Script: This script contains functions for reading
tidal data, processing it, and performing a variety of tidal analysis.
"""

# import modules needed here
import argparse
import os
import glob
import numpy as np
import pandas as pd
import uptide
from scipy import stats

# uppercase variable name used
# for naming data1 as a constant
DATA1 = "data/1947ABE.txt"

def read_tidal_data(data1):

    """Reads 1947 Aberdeen tidal data from a 
    file and returns a DataFrame."""

    # read and import data
    # https://www.geeksforgeeks.org/pandas-read_table-function/
    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    # ignoring header and naming columns
    data1 = pd.read_table(data1, skiprows=11,
                          names=["Cycle", "Date", "Time", "Sea Level", "Residual"], sep=r'\s+')
    # combining date and time columns
    # https://scales.arabpsychology.com/stats/how-do-i-combine-two-date-and-time-columns-into-one-in-a-pandas-dataframe/
    data1["DateTime"] = pd.to_datetime(data1["Date"] + ' ' + data1["Time"])
    # dropping unnecessary columns
    data1 = data1.drop(["Cycle", "Date", "Time", "Residual"], axis = 1)
    # setting datetime as index
    data1 = data1.set_index("DateTime")
    # removing M, N, and T data
    data1.replace(to_replace=".*[MNT]$",value={'Sea Level':np.nan},regex=True,inplace=True)
    # converting sea level column from object to float
    # https://sentry.io/answers/change-a-column-type-in-a-dataframe-in-python-pandas/#:~:text=If%20we%20want%20to%20convert,should%20use%20the%20to_numeric%20function.
    data1["Sea Level"] = data1["Sea Level"].astype(float)

    return data1

def extract_single_year_remove_mean(year, data1):

    """Extracts a complete year from 1947 
    Aberdeen DataFrame and removes the mean."""

    year = 1947
    # define start and end of datetime index
    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
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

    # variable will only lock on the date/time supplied
    year1946_47 = data.loc[start:end]
    # calculate mean of data supplied
    mean_sea_level = np.mean(year1946_47["Sea Level"])
    # remove mean to oscillate around zero
    year1946_47["Sea Level"] -= mean_sea_level

    return year1946_47

def join_data(data1, data2):

    """Reads 1946 Aberdeen and 
    joins together with 1947 Aberdeen."""

    # read and format 1946 Aberdeen txtfile through function
    data2 = read_tidal_data("data/1946ABE.txt")
    # join two dataframes together
    # https://saturncloud.io/blog/pandas-how-to-concatenate-dataframes-with-different-columns/
    data = pd.concat([data2, data1])

    return data

def sea_level_rise(data):

    """Calculates the linear regression of sea level 
    rise over time and returns slope and p-value."""

    # filtering out NaN values from combined dataset
    filtered_data = data.dropna()
    # extracting both index of filtered dataframe and Sea level column,
    # converting it into a NumPy array, required for a linregression.
    # https://stackoverflow.com/questions/13187778/convert-pandas-dataframe-to-numpy-array
    hours = filtered_data.index.to_numpy()
    sea_level = filtered_data["Sea Level"].to_numpy()
    # linear regression equation divided by the
    # number of seconds in a day to find rise per day
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html
    slope, _, _, p_value, _  = stats.linregress(hours.astype('int64' ) / 86400, sea_level)

    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):

    """Performs harmonic analysis on 
    tidal data and returns M2 and S2."""

    # create new filtered dataframe
    data3 = data.dropna()
    # extract min and max dates from dataframe index
    # https://stackoverflow.com/questions/23178129/getting-min-and-max-dates-from-a-pandas-dataframe
    # and format them as strings to be universal with other dataframes
    # https://sparkbyexamples.com/pandas/convert-pandas-datetimeindex-to-string/
    start_date = data3.index.min().strftime('%Y-%m-%d')
    end_date = data3.index.max().strftime('%Y-%m-%d').strip()
    # remove mean from dataframe with function
    section = extract_section_remove_mean(start_date, end_date, data3)
    # creating a tide variable with constituents
    # making it ready for tidal analysis
    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    tide = uptide.Tides(constituents)
    # setting initial time given for calculations
    tide.set_initial_time(start_datetime)
    # calculate seconds since initial time given
    seconds_since = (section.index.astype('int64').to_numpy()/1e9) - start_datetime.timestamp()
    # perform harmonic analysis
    amp,pha = uptide.harmonic_analysis(tide, section["Sea Level"].to_numpy(), seconds_since)

    return amp,pha

#def get_longest_contiguous_data(data):

    #"""Gets the longest
    #contiguous period of data."""

    #return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Ruben A. Freire"
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

    # use glob to find txt files in desired directory
    # https://www.delftstack.com/howto/python/read-multiple-csv-files-in-python/
    all_files = glob.glob(os.path.join(dirname, "*.txt"))

    # read and join data files one by one to an empty dataframe
    # https://www.delftstack.com/howto/python/read-multiple-csv-files-in-python/
    all_data = pd.DataFrame()
    for filename in all_files:
        data_outer = read_tidal_data(filename)
        all_data = pd.concat([all_data, data_outer])

    # filter out NaN values
    all_data = all_data.dropna()

    # ensure index is DateTime
    all_data = all_data.sort_index()

    # print station name
    print("\nStation name:" + " " + (dirname))

    # print head and tail of given tidal data
    print("\nTidal Data:")
    print(all_data)

    # calculate and print sea level rise
    gradient, p_val = sea_level_rise(all_data)
    print("\nSea Level Rise over time (m):")
    print("Slope:", gradient)
    print("p-value:", p_val)

    # perform and print tidal analysis
    datetime = all_data.index.min()
    amp_outer,pha_outer = tidal_analysis(all_data, ['M2', 'S2'], datetime)
    print("\nTidal Analysis (m):")
    print("M2 Amplitude:", amp_outer[0])
    print("S2 Amplitude:", amp_outer[1])
