
"""
TODO document this
"""


def nomis_fetch_dataset(dataset, filters, encoding=None):
    import pandas as pd

    page = 1
    api_url = "https://www.nomisweb.co.uk/api/v01/dataset/" + \
        dataset + ".data.csv?recordlimit=25000"

    for (attr, value) in filters.items():
        api_url = api_url + "&" + attr + "=" + value
    res = pd.read_csv(api_url, header=0, encoding=encoding)
    df = res
    while (len(res) == 25000):
        url = api_url+"&recordoffset=" + str(25000 * page)
        res = pd.read_csv(url, header=0, encoding=encoding)
        page += 1
        df = pd.concat([df, res])

    return df

# return dataset with just list of geographies and values


def nomis_geography(df, title="Value"):
    df = df[['GEOGRAPHY_NAME', 'OBS_VALUE']]
    df = df.dropna()
    df = df.rename(columns={"GEOGRAPHY_NAME": "Area", "OBS_VALUE": title})

    return df

# return dataset with just list of years and values


def nomis_years(df, title="Value"):
    df = df[['DATE_NAME', 'OBS_VALUE']]
    df = df.dropna()
    df = df.rename(columns={"DATE_NAME": "Year", "OBS_VALUE": title})

    return df
