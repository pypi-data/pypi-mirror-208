import logging
import os

logger = logging.getLogger(__name__)

# Set the logging level by environment variable
logging_level = os.environ.get('LOGLEVEL') or 'INFO'
logging.basicConfig(level=logging_level,
                    format='%(levelname)s %(message)s')


def get_all_datasets():
    # Returns all the datasets available on the ONS API. Also goes and fetches the latest download link (ie most recent version) and the geographic resolution.
    # Not sure you'll ever need to use this really, but it's useful for building the dataset list right now.
    import requests
    datasets = []
    api_result = {
        'items': []
    }
    # keep hitting the ONS API and appending the data to the array
    limit = 1000
    while len(api_result['items']) == limit or len(datasets) == 0:
        api_result = requests.get(
            'https://api.beta.ons.gov.uk/v1/datasets?limit=' + str(limit) + '&offset=' + str(len(datasets))).json()
        datasets += (api_result['items'])

    # embellish the datasets with extra data
    for dataset in datasets:
        url = dataset['links']['latest_version']['href']
        dataset_api_result = requests.get(url).json()
        if 'downloads' in dataset_api_result.keys():
            if 'csv' in dataset_api_result['downloads'].keys():
                dataset['download'] = dataset_api_result['downloads']['csv']['href']
            elif 'xls' in dataset_api_result['downloads'].keys():
                dataset['download'] = dataset_api_result['downloads']['xls']['href']
        dataset['dimensions'] = dataset_api_result['dimensions']
        for dimension in dataset['dimensions']:
            if (dimension['name'] == 'geography'):
                dataset['geography'] = dimension['id']

    return datasets


def quick_data(id, filters):
    """"
    fetches a dataset from the ONS API, and returns a pandas dataframe, with the filters applied
    """
    import requests
    import pandas as pd
    filters = build_filter(id, filters)
    dataset_url = "https://api.beta.ons.gov.uk/v1/datasets/" + id
    dataset_metadata = requests.get(dataset_url).json()
    latest_version = dataset_metadata['links']['latest_version']['href']
    data_url = latest_version + "/observations?"

    for key in filters.keys():
        data_url += key + "=" + str(filters[key]) + "&"

    dataset = requests.get(data_url).json()
    df = pd.json_normalize(dataset['observations'])

    good_columns = ['observation']
    for col in df.columns:
        bits = col.split('.')
        if bits[-1] == 'label':
            df = df.rename(columns={col: bits[1]})
            good_columns.append(bits[1])
    df = df[good_columns]
    df = df.rename(columns={"observation": dataset['unit_of_measure']})
    return df


def get_dimensions(id):
    # returns the dimensions of a dataset, and the options for each dimension
    import requests
    dataset_url = "https://api.beta.ons.gov.uk/v1/datasets/" + id
    dataset_metadata = requests.get(dataset_url).json()
    latest_version = dataset_metadata['links']['latest_version']['href']
    d_url = latest_version + "/dimensions"
    dimensions = requests.get(d_url).json()
    return dimensions['items']


def get_options(id):
    import requests
    dimensions = get_dimensions(id)
    out = []
    for dimension in dimensions:
        options_result = requests.get(
            dimension['links']['options']['href'] + "?limit=1000").json()
        options = []
        for option in options_result['items']:
            options.append(option['option'])
        out.append({
            str(dimension['name']): options
        })
    return out


def build_filter(dataset, filters):
    import requests
    dimensions = get_dimensions(dataset)
    for dimension in dimensions:
        # print(dimension['links']['options']['href'])
        if dimension['name'] not in filters.keys():
            options = requests.get(
                dimension['links']['options']['href']).json()
            for options in options['items']:
                if options['option'] == 'all' or options['option'] == 'total':
                    filters[dimension['name']] = options['option']
                    break
    return filters


def build_dimensions(dimensions):
    # builds the dimensions part of the POST request
    new_dimensions = []
    for dimension in dimensions.keys():
        if type(dimensions[dimension]) is str:
            new_dimensions.append({
                "name": dimension,
                "options": [dimensions[dimension]]
            })
        else:
            new_dimensions.append({
                "name": dimension,
                "options": dimensions[dimension]
            })
    return new_dimensions


def get_dataset(dataset, dimensions):
    # POST to ONS with a filter, and get the data back
    import requests
    import pandas as pd
    import time
    import io

    dataset_url = "https://api.beta.ons.gov.uk/v1/datasets/" + dataset
    dataset_metadata = requests.get(dataset_url).json()
    latest_version = dataset_metadata['links']['latest_version']['href']
    logger.info('Found latest version of dataset ' + dataset)
    latest_version_metadata = requests.get(latest_version).json()
    post_data = {
        "dataset": {
            "id": dataset,
            "edition": latest_version_metadata['edition'],
            "version": latest_version_metadata['version']
        },
        "dimensions": build_dimensions(dimensions),
    }

    logger.info('Posting filter...')
    filter_metadata = requests.post(
        "https://api.beta.ons.gov.uk/v1/filters?submitted=true", json=post_data).json()
    output_url = filter_metadata['links']['filter_output']['href']

    logger.info('Waiting for ONS to prepare download...')
    download_metadata = requests.get(output_url).json()
    while download_metadata['state'] == 'created':
        time.sleep(1)
        download_metadata = requests.get(output_url).json()

    logger.info('Downloading file...')
    download_url = download_metadata['downloads']['csv']['href']
    csv = requests.get(download_url)
    df = pd.read_csv(io.StringIO(csv.text))
    logger.info('Download complete')

    return df
