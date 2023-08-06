import pandas as pd
from requests import get, exceptions
import datetime
import os

class NoAuthorization(Exception):
    def __init__(self, message="You're not authorized! Please call auth() method with a valid authorization key"):
        self.message = message
        super().__init__(self.message)

class DataGetter():
    _URL = 'https://alt-data-api.azurewebsites.net/api/macro/get'
    _API_KEY = ''
    
    def _set_url(self, url):
        self._URL = url
    
    def _prettify_indicators(self, ind_list):
        return [" ".join([name.capitalize() if name not in ['gdp', 'cpi'] else name.upper() for name in indicator.split("_")]) for indicator in ind_list]

    def _api_call(self, **kwargs):
        if self._API_KEY == '': raise NoAuthorization()

        params = { k:v for k,v in kwargs.items() if len(v) > 0 }
        try:
            api_response = get(url=self._URL, params=params, headers={ 'AD-Api-Key': self._API_KEY })
            return api_response
        except exceptions.Timeout:
            return "API server doesn't respond"
        except exceptions.ConnectionError:
            return "Network connection error"
    
    def auth(self, token=''):
        self._API_KEY = token
        response = self._api_call(frequency='Yearly', country='Tajikistan')
        if response.status_code == 403:
            print('Invalid authorization key')
            self._API_KEY = ''


    def get_data(self, **kwargs):
        if 'start' in kwargs.keys():
            try: datetime.date.fromisoformat(kwargs['start']) 
            except ValueError: 
                print("Dates should be provided in YYYY-MM-DD format!")
                return
        if 'end' in kwargs.keys():
            try: datetime.date.fromisoformat(kwargs['end']) 
            except ValueError: 
                print("Dates should be provided in YYYY-MM-DD format!")
                return
                
        if not 'country' in kwargs.keys():
            print('Provide the country to get data for')
            return

        try:
            data = self._api_call( country = kwargs['country'], frequency = kwargs.get('frequency') or '' )
        except NoAuthorization as e:
            print(e.message)
            return
        
        data = data.json()
        if len(data) == 0: 
            print('Invalid country name.')
            return
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        if 'start' in kwargs.keys() or 'end' in kwargs.keys():
            if 'start' in kwargs.keys() and not 'end' in kwargs.keys():
                mask = (df['date'] >= kwargs['start'])
            elif not 'start' in kwargs.keys() and 'end' in kwargs.keys():
                mask = (df['date'] <= kwargs['end'])
            else: 
                mask = (df['date'] >= kwargs['start']) & (df['date'] <= kwargs['end'])
            df = df.loc[mask]
            if len(df) == 0: 
                print('Start or end date are out of bounds.')
                return
        df.columns = self._prettify_indicators(df.columns)
        df.to_csv("%s/%s_macrodata.csv" % (os.getcwd(), kwargs['country']), header=df.columns, index=False)
        return
    
    def get_countries(self):
        try: data = self._api_call(frequency="Yearly").json()
        except NoAuthorization as e: 
            print(e.message) 
            return
        
        entirety = pd.DataFrame(data)
        countries = pd.DataFrame({'Country name': entirety['country'].unique()})
        countries.to_csv('%s/supported_countries.csv' % os.getcwd(), index=False)
        return

    def get_indicators(self, **kwargs):
        try: data = self._api_call(country=kwargs.get('country') or '').json()
        except NoAuthorization as e: 
            print(e.message)
            return
        
        if len(data) == 0: 
            print('Invalid country name.')
            return

        entirety = pd.DataFrame(data)
        indicators = pd.DataFrame({'Indicator name': self._prettify_indicators([name for name in entirety.columns if name not in ['date', 'country']])})
        indicators.to_csv('%s/indicators.csv' % os.getcwd(), index=False)
        return