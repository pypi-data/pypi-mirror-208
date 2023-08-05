import logging
import os
import requests
import hashlib
import pandas as pd
import io
from . import api
from . import utils

logger = logging.getLogger(__name__)

# Set the logging level by environment variable
logging_level = os.environ.get('LOGLEVEL') or 'INFO'
logging.basicConfig(level=logging_level,
                    format='%(levelname)s %(message)s')

# ----------------------
# Convenience functions wrapping the client object
# ----------------------


def no_cache():
    return os.environ.get('DATAPRESS_NO_CACHE', 'false').lower() == 'true'


def get_dataset(id=None):
    env_dataset = os.environ.get('DATAPRESS_DATASET', None)
    if (env_dataset is not None and id is not None and env_dataset != id):
        raise Exception(
            f'Clash between get_dataset(id={id}) and DATAPRESS_DATASET={env_dataset}. Use one or the other!')
    id = id or env_dataset
    if not id:
        raise ValueError(
            'No dataset id provided, and DATAPRESS_DATASET not set')
    # --
    return Dataset(id)


def _get_column_type(t):
    """Simplify column types to a few basic types"""
    if t == 'int64' or t == 'float64':
        return 'number'
    if str(t).startswith('datetime'):
        return 'datetime'
    return 'string'


def _get_column_metadata(df):
    df = df.head(10)
    out = []
    # Get the first 40 columns (that should be enough)
    for col_name in df.columns[:40]:
        col_type = _get_column_type(df[col_name].dtype)
        out.append({
            'name': col_name[:255],
            'type': str(col_type),
        })
    return out


# ----------------------
# Used to interact with a dataset
# ----------------------
class Dataset:
    def __init__(self, id):
        """
        Fetch a dataset from DataPress.
        """
        self.id = id
        self.refresh()

        logger.info('Loaded dataset %s: "%s"', self.id, self.json['title'])

    def refresh(self):
        """
        Refresh the dataset metadata from the website.
        """
        self.json = api.get('/api/dataset/' + self.id)

    def load_dataframe(self, resource_id):
        """
        Fetch a file from the dataset and return it as a Pandas DataFrame.
        """
        if not resource_id in self.json['resources']:
            raise ValueError(
                f'Dataset does not contain resource {resource_id}')
        url = self.json['resources'][resource_id]['url']
        logger.debug('Loading resource %s from %s', resource_id, url)
        # --
        r = requests.get(url + '?redirect=true', headers={
            'Authorization': api.get_conn().api_key
        })
        assert r.status_code == 200, 'Failed to load resource %s' % resource_id
        # Open a pandas dataframe:
        origin = self.json['resources'][resource_id]['origin']
        extension = os.path.splitext(origin.lower())[1]
        if extension == '.xlsx' or extension == '.xls':
            xls = pd.ExcelFile(io.BytesIO(r.content))
            out = {}
            for sheet in xls.sheet_names:
                # add the sheet to out
                out[sheet] = pd.read_excel(xls, sheet)
            return out
        elif extension == '.csv':
            return pd.read_csv(io.StringIO(r.text), on_bad_lines='warn')
        elif extension == '.ods':
            xls = pd.ExcelFile(io.BytesIO(r.content))
            out = {}
            for sheet in xls.sheet_names:
                # add the sheet to out
                out[sheet] = pd.read_excel(xls, sheet, engine='odf')
            return out
        else:
            # Unrecognised file type
            return None

    def load_dataframes(self, keys='files'):
        """
        Fetch all the dataset's files as pandas DataFrames.
        Grabs any file with attachment=false.

        Argument:
        keys -- 'files' (default): Index the dataframes by original filename
             -- 'ids': Index the dataframes by resource IDs

        Loads all the resources listed on the script in the DataPress UI.
        (Indexed by filename and also by resource ID).
        """
        self.refresh()
        assert keys in ['files', 'ids']

        # Load the script
        if not 'script' in self.json:
            raise Exception('Dataset does not contain a script')

        # There is a dict on dataset['resources'].
        # Get all the dict keys where the value is an object which has attachment=False
        resource_ids = [k for k, v in self.json['resources'].items()
                        if v['attachment'] == False]

        out = {}
        for (i, id) in enumerate(resource_ids):
            # Get the filename (decoding the URL)
            origin = self.json['resources'][id]['origin']
            filename = origin.split('/')[-1]
            logger.info('Downloading file %d of %d: %s', i + 1,
                        len(resource_ids), filename)
            df = self.load_dataframe(resource_ids[i])
            if df is None:
                logger.info('Skipping unrecognised file type: %s', filename)
            else:
                key = filename if keys == 'files' else id
                out[key] = df
        return out

    def _commit_csv(self, csv_data, name, type):
        """
        Private method: Upload a table or chart via a pre-signed link
        """
        assert type in ['table', 'chart', 'table.sample']

        # Request a presigned upload from the website, at
        # /api/dataset/:id/presign/script/table/:table_id
        presign_path = '/'.join([
            'api',
            'dataset',
            self.id,
            'presign',
            'script',
            type,
            name,
        ])
        presign = api.post(presign_path)

        # Response format:
        # {
        #   "url": "https://ams3.digitaloceanspaces.com/datapress-files",
        #   "fields": {
        #     "bucket": "datapress-files",
        #     "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        #     "X-Amz-Credential": "[credential]",
        #     "X-Amz-Date": "[date]",
        #     "key": "[path to upload]",
        #     "Policy": "[hashed policy]",
        #     "X-Amz-Signature": "[my signature]"
        #   }
        # }

        # Upload the file to the one-time URL
        url = presign['url'] + presign['fields']['bucket']
        logger.debug('POST %s', url)
        requests.post(url, data=presign['fields'], files={
            'file': csv_data
        })
        return presign['fields']['key']

    def commit_table(self, name, df):
        """
        Upload a table to DataPress.
        Provide a kebab-case-name for the table, and a pandas dataframe.
        """
        if utils.check_key_for_errors(name) is not None:
            raise Exception('Invalid table name: "' + name +
                            '": ' + utils.check_key_for_errors(name))

        self.refresh()
        tables = self.json['script']['tables']
        csv_data = df.to_csv(index=False).encode('utf-8')

        # Get the first 100 rows and the first 40 columns
        csv_sample_data = df[df.columns[:40]].head(
            100).to_csv(index=False).encode('utf-8')
        column_metadata = _get_column_metadata(df)

        # Deduplicate
        if name in tables:
            old_hash = tables[name]['csvHash']
            new_hash = hashlib.md5(csv_data).hexdigest()
            if old_hash == new_hash:
                if no_cache():
                    logger.info(
                        'Overwriting table: "%s" (CSV is unchanged, NO_CACHE=true)', name)
                else:
                    logger.info(
                        'Skipping table: "%s" (CSV is unchanged)', name)
                    return

        logger.info('Uploading table: "%s"', name)

        csv_key = self._commit_csv(csv_data, name, 'table')
        csv_sample_key = self._commit_csv(
            csv_sample_data, name, 'table.sample')

        # Fetch the dataset metadata
        path = "/script/tables/" + name
        if name not in tables:
            logger.info('Creating table "%s" on the dataset', name)
            api.patch('/api/dataset/' + self.id, [
                {   # Add the table
                    "op": "add",
                    "path": path,
                    "value": {
                        'csv': csv_key,
                        'csvSample': csv_sample_key,
                        'columns': column_metadata,
                        'rowCount': len(df),
                    }
                }
            ])
        else:
            logger.info('Updating table "%s" on the dataset', name)
            api.patch('/api/dataset/' + self.id, json=[
                {   # Update the script's table key on DataPress
                    "op": "add",
                    "path": path + '/csv',
                    "value": csv_key
                },
                {
                    "op": "add",
                    "path": path + '/csvSample',
                    "value": csv_sample_key
                },
                {
                    "op": "add",
                    "path": path + '/columns',
                    "value": column_metadata
                },
                {
                    "op": "add",
                    "path": path + '/rowCount',
                    "value": len(df),
                }
            ])

    def commit_chart(self, name, df):
        """
        Upload a table to DataPress.

        Provide a kebab-case-name for the table, and a pandas dataframe.
        The output CSV must be under 100kb.
        """
        if utils.check_key_for_errors(name) is not None:
            raise Exception('Invalid chart name: "' + name +
                            '": ' + utils.check_key_for_errors(name))

        self.refresh()
        charts = self.json['script']['charts']
        csv_data = df.to_csv(index=False).encode('utf-8')

        # Deduplicate
        if name in charts:
            old_hash = charts[name]['csvHash']
            new_hash = hashlib.md5(csv_data).hexdigest()
            if old_hash == new_hash:
                if no_cache():
                    logger.info(
                        'Overwriting chart: "%s" (CSV is unchanged, NO_CACHE=true)', name)
                else:
                    logger.info(
                        'Skipping chart: "%s" (CSV is unchanged)', name)
                    return

        # Verify we can chart this at all
        logger.info('Uploading chart: "%s"', name)
        if (len(csv_data) > 1024 * 100):
            raise Exception('Chart CSV data must be under 100kb')

        csv_key = self._commit_csv(csv_data, name, 'chart')

        path = "/script/charts/" + name
        if name not in charts:
            logger.info('Creating chart "%s" on the dataset', name)
            api.patch('/api/dataset/' + self.id, [
                {   # Add the chart
                    "op": "add",
                    "path": path,
                    "value": {'csv': csv_key}
                }
            ])
        else:
            # Update the script's table key on DataPress
            logger.info('Updating chart "%s" on the dataset', name)
            api.patch('/api/dataset/' + self.id, [
                {
                    "op": "add",
                    "path": path + '/csv',
                    "value": csv_key
                }
            ])
