import logging
import os
import requests
import dotenv

# Load .env in cwd
dotenv.load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

logger = logging.getLogger(__name__)

# Set the logging level by environment variable
logging_level = os.environ.get('LOGLEVEL') or 'INFO'
logging.basicConfig(level=logging_level,
                    format='%(levelname)s %(message)s')

# Cached instance of Conn for this script run
_conn = None


def get_conn():
    global _conn
    if _conn is None:
        _conn = Conn()
    return _conn


def get(path, params=None):
    return get_conn().request('GET', path, params=params)


def patch(path, json=None):
    return get_conn().request('PATCH', path, json=json)


def post(path, json=None):
    return get_conn().request('POST', path, json=json)


class Conn:
    def __init__(self):
        """
        Create an API connection to DataPress. Uses env:

        * DATAPRESS_URL
        * DATAPRESS_API_KEY
        """
        if os.environ.get('DATAPRESS_URL') is None:
            raise ValueError('Missing environment variable DATAPRESS_URL')
        # --
        self.site_url = os.environ['DATAPRESS_URL']
        self.api_key = os.environ.get('DATAPRESS_API_KEY', None)
        # ---
        # Check the connection
        r = requests.get(self.site_url + '/api/context', headers={
            'Authorization': self.api_key
        })
        if (r.status_code != 200):
            raise Exception(
                f'Error connecting to DataPress: {r.status_code}')
        context = r.json()
        logger.info('Connected to DataPress at %s',
                    context['site']['hostname'])
        self.site = context['site']
        if self.api_key is not None:
            if context.get('user') is None:
                raise Exception('Unrecognised API Key')
            else:
                logger.info('Connected as %s', context['user']['email'])
                self.user = context.get('user')
        else:
            logger.info('(Not logged in, no DATAPRESS_API_KEY set)')
            self.user = None

    def request(self, method, path, params=None, json=None):
        assert method in ['GET', 'POST', 'PATCH', 'DELETE']
        if (method in ['POST', 'PATCH', 'DELETE'] and self.api_key is None):
            raise Exception('Missing environment variable DATAPRESS_API_KEY')
        if (not path.startswith('/')):
            path = '/' + path
        url = self.site_url + path
        r = requests.request(method, url, json=json, params=params,
                             headers={
                                 'Authorization': self.api_key
                             })
        if (r.status_code != 200):
            try:
                # format the JSON nicely
                print(json.dumps(r.json(), indent=2))
            except:
                print(r.text)
            raise Exception(
                f'{r.status_code} on {method} {url}')
        return r.json()
