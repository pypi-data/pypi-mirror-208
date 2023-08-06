import urllib.parse

from requests import exceptions,codes,Session
from requests.auth import HTTPBasicAuth,AuthBase
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import ConnectionError, ConnectTimeout

#from requests.packages.urllib3.util.retry import Retry

from cast_common.logger import Logger,INFO, ERROR
from pandas import DataFrame
from time import perf_counter, ctime

__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2022, CAST Software"

class HTTPBearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r

class RestCall(Logger):

    _base_url = None
    _auth = None
    _time_tracker_df  = DataFrame()
    _track_time = True

    def __init__(self, base_url, user=None, password=None, track_time=False,log_level=INFO,accept_json=True):
        super().__init__(level=log_level)
        if base_url[-1]=='/': 
            base_url=base_url[:-1]
        self._base_url = base_url
        self._track_time = track_time

        self._session = Session()
        self._max_retries = 5

        self._accept_json = accept_json

        self._adapter = HTTPAdapter(
                max_retries = Retry(
                    total = self._max_retries,
                    backoff_factor = 1,
                    status_forcelist = [408, 500, 502, 503, 504],
                )
        )

        self._session.mount('http://', self._adapter)
        self._session.mount('https://', self._adapter)
        
        if user == '__token__':
            self._auth = HTTPBearerAuth(password)
        else:
            self._auth = HTTPBasicAuth(user, password)

        #self._session.headers.update({'Accept': 'application/json'})

        #self._session.headers.update({'Authorization': self._auth})

    def post(self, url = "",params:dict={},header:dict={}):
        try:
            if len(url) > 0 and url[0] != '/':
                url=f'/{url}'
            u = urllib.parse.quote(f'{self._base_url}{url}',safe='/:&?=')

            #header = {}
            if self._accept_json:
                header['Accept']='application/json'
            resp = self._session.post(u,params, timeout = (5, 15),auth=self._auth,headers=header)

            resp.raise_for_status()

            if resp.status_code == codes.ok:
                return resp.status_code, resp.json()
            else:
                return resp.status_code,""
            
        except exceptions.ConnectionError as ex:
            self.error(f'Unable to connect to host {self._base_url} ({ex})')
        except exceptions.Timeout as ex:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error(f'Timeout while performing api request using: {url} ({ex})')
        except exceptions.TooManyRedirects as ex:
            #TODO Tell the user their URL was bad and try a different one
            self.error(f'TooManyRedirects while performing api request using: {url} ({ex})')
        except exceptions.HTTPError as e:
            self.error(e)
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error(f'General Request exception while performing api request using: {u} ({e})')
            raise e


    def get(self, url = "",header=None):
        start_dttm = ctime()
        start_tm = perf_counter()

        try:
            if len(url) > 0 and url[0] != '/':
                url=f'/{url}'
            u = urllib.parse.quote(f'{self._base_url}{url}',safe='/:&?=')
            # if self._auth == None:
            #     resp = get(url= u, headers={'Accept': 'application/json'})
            # else:
            #     resp = get(url= u, auth = self._auth, headers={'Accept': 'application/json'})

            header = {}
            if self._accept_json:
                header['Accept']='application/json'
            resp = self._session.get(u, timeout = (5, 15),auth=self._auth,headers=header)

            resp.raise_for_status()

            # Save the duration, if enabled.
            if (self._track_time):
                end_tm = perf_counter()
                end_dttm = ctime()
                duration = end_tm - start_tm

                #print(f'Request completed in {duration} ms')
                self._time_tracker_df = self._time_tracker_df.append({'Application': 'ALL', 'URL': url, 'Start Time': start_dttm \
                                                            , 'End Time': end_dttm, 'Duration': duration}, ignore_index=True)
            if resp.status_code == codes.ok:
                return resp.status_code, resp.json()
            else:
                return resp.status_code,""

        except exceptions.ConnectionError as ex:
            self.error(f'Unable to connect to host {self._base_url} ({ex})')
        except exceptions.Timeout as ex:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error(f'Timeout while performing api request using: {url} ({ex})')
        except exceptions.TooManyRedirects as ex:
            #TODO Tell the user their URL was bad and try a different one
            self.error(f'TooManyRedirects while performing api request using: {url} ({ex})')
        except exceptions.HTTPError as e:
            self.error(e)
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error(f'General Request exception while performing api request using: {u} ({e})')
            raise e

        return 0, "{}"
