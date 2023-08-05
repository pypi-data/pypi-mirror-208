import os
import pandas as pd

# datapress_client directory
DIRNAME = os.path.dirname(os.path.abspath(__file__))

"""
List the LSOAs in a given header region (as numpy array)
"""


def get_lsoas_in(place):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    frame = frame[frame['UTLA19NM'] == place]
    return frame['LSOA11CD'].unique()


"""
List the LADs in a given header region (as numpy array)
"""


def get_lads_in(place):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    frame = frame[frame['UTLA19NM'] == place]
    return frame['LAD19CD'].unique().tolist()


def get_wards_in(place):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    frame = frame[frame['UTLA19NM'] == place]
    return frame['LAD19CD'].unique().tolist()


def get_geography_code(place):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    frame = frame[frame['UTLA19NM'] == place]
    return frame['UTLA19CD'].unique().tolist()


def get_region(place):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    frame = frame[frame['UTLA19NM'] == place]
    regions = frame['RGN11CD'].unique().tolist()
    # This should really only return one region, but just in case...
    if len(regions) > 1:
        raise Exception("More than one region found for " + place)
    return regions[0]


def get_geographies_of(place, type, type_of_place=None):
    match type:
        case 'lsoa codes':
            type = 'LSOA11CD'
        case 'lsoas':
            type = 'LSOA11NM'
        case 'msoa codes':
            type = 'MSOA11CD'
        case 'msoas':
            type = 'MSOA11NM'
        case 'ward codes':
            type = 'WD19CD'
        case 'wards':
            type = 'WD19NM'
        case 'constituency codes':
            type = 'PCON19CD'
        case 'constituencies':
            type = 'PCON19NM'
        case 'lad codes':
            type = 'LAD19CD'
        case 'lads':
            type = 'LAD19NM'
        case 'authority codes':
            type = 'UTLA19CD'
        case 'authorities':
            type = 'UTLA19NM'
        case 'region codes':
            type = 'RGN11CD'
        case 'regions':
            type = 'RGN11NM'
        case 'country code':
            type = 'CTRY11CD'
        case 'country':
            type = 'CTRY11NM'
        case 'nomis codes':
            type = 'NOMISCD'

    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename, dtype=str)
    for col in frame.columns:
        list = frame[col].unique().tolist()
        if place in list:
            type_of_place = col
            break
    frame = frame[frame[type_of_place] == place]
    return frame[type].unique().tolist()


def get_regions(names=False):
    filename = os.path.join(DIRNAME, 'static', 'lsoa_lookup.csv')
    frame = pd.read_csv(filename)
    if names:
        return frame['RGN11NM'].unique().tolist()
    else:
        return frame['RGN11CD'].unique().tolist()
