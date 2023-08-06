from cast_common.restAPI import RestCall
from cast_common.logger import INFO
from cast_common.util import format_table

from requests import codes
from pandas import ExcelWriter,DataFrame


class Highlight(RestCall):

    _data = []
    _apps = []
    _tags = []
    _cloud = []
    _oss = []
    _elegance = []
    _instance_id = None

    def __init__(self,  hl_user:str, hl_pswd:str, 
                 hl_instance:int,hl_apps:str=[],hl_tags:str=[], 
                 hl_base_url:str='https://rpa.casthighlight.com', 
                 log_level=INFO, timer_on=False):

        super().__init__(f'{hl_base_url}/WS2/', hl_user, hl_pswd, timer_on,log_level,accept_json=False)

        self._hl_instance = hl_instance

        self._business = self._get_top_metric('businessValue')
        self._cloud = self._get_top_metric('cloudValue')
        self._oss = self._get_top_metric('openSourceSafty')
        self._elegance = self._get_top_metric('softwareElegance')

        self._tags = self._get_tags()
        self._apps = DataFrame(self._get_applications())
        self.info(f'Found {len(self._apps)} applications')
        self._apps.dropna(subset=['metrics'],inplace=True)
        self.info(f'Found {len(self._apps)} analyzed applications')
        if len(hl_apps) > 0:
            self._apps = self._apps[self._apps['name'].isin(hl_apps)]
        self.info(f'{len(self._apps)} applications selected')

        for app in hl_apps:
            try:
                self._data[app]=self._get_application_data(app)
            except KeyError as ke:
                
                
        pass


        # file_name = r'e:/work/wellsfargo/tags.xlsx'
        # writer = ExcelWriter(file_name, engine='xlsxwriter')
        # summary_tab = format_table(writer,DataFrame(self._tags),'Tags')
        # writer.close()


        pass

    def _get(self,url:str) -> DataFrame:
        (status, json) = self.get(url)
        if status == codes.ok:
            return DataFrame(json)
        else:
            raise KeyError (f'Server returned a {status} while accessing {url}')

    def _get_applications(self):
        return self._get(f'domains/{self._hl_instance}/applications/')
        
    def _get_tags(self) -> DataFrame:
        return DataFrame(self._get(f'domains/{self._hl_instance}/tags/'))

    def _get_top_metric(self,metric:str) -> DataFrame:
        return DataFrame(self.post(f'domains/{self._hl_instance}/metrics/top?metric=cloudReady&order=desc',header={'Content-type':'application/json'}))

    def _get_application_data(self,app:str) -> dict:
        return self._get(f'domains/{self._hl_instance}/applications/{self.get_app_id(app)}')

    def get_app_id(self,app_name):
        url = f'domains/{self._hl_instance}/applications/'
        (status, json) = self.get(url)

        # TODO: Handle exceptions
        if status == codes.ok and len(json) > 0:
            for id in json:
                if id['name'].lower()==app_name.lower():
                    return id['id']
            raise KeyError (f'Highlight application not found: {app_name}')



#hl = Highlight('n.kaplan+EYInternal@castsoftware.com','vadKpBFAZ8KIKb2f2y',20373,hl_apps=['1AAT:web','1AES:entitlement-composite-v1'])
hl = Highlight('n.kaplan+EYInternal@castsoftware.com','vadKpBFAZ8KIKb2f2y',20373)
    