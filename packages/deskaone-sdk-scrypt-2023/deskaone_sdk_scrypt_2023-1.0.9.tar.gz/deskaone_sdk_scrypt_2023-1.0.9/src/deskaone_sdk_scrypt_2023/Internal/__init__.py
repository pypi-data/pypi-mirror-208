import json
from requests.exceptions import ConnectionError, ConnectTimeout, ProxyError, ReadTimeout, JSONDecodeError, TooManyRedirects
import requests
from deskaone_sdk_scrypt_2023.Exceptions import Error


class Internal:
    
    def __init__(self, *args, **kwargs) -> None:
        """A Internal Requests.
        
        Basic Usage::

            Internal(
                URL     = str,
                PARAMS  = str,
                HEADERS = dict
            )
            
        params is Json/urlencode for POST/PUT or urlencode for GET
        """
        self.URL        = kwargs.get('URL')
        self.PARAMS     = kwargs.get('PARAMS')
        self.HEADERS    = kwargs.get('HEADERS')
        self.Session    = requests.Session()        
    
    def Setup(self, *args, **kwargs):
        """A Internal Requests.
        
        Basic Usage::

            Internal(
                URL     = str,
                PARAMS  = str | JSON | URLENCODE,
                HEADERS = dict
            ).Setup(
                PROXIES = dict,
                METHODS = str | POST | GET | PUT, | default GET
                TIMEOUT = int | default 15 seconds
            )
            
        params is Json/urlencode for POST/PUT or urlencode for GET
        
        MODE POST/PUT/GET default GET
        
        Basic Return::

            return text: str
            
        """
        
        self.PROXIES    = dict() if kwargs.get('PROXIES') is None else dict(kwargs.get('PROXIES'))
        self.METHODS    = 'GET' if kwargs.get('METHODS') is None else kwargs.get('METHODS')
        self.TIMEOUT    = 15 if kwargs.get('TIMEOUT') is None else kwargs.get('TIMEOUT')
        self.Session.proxies     = self.PROXIES
            
        try:
            if self.METHODS == 'POST':Result = self.Session.post(self.URL, data=self.PARAMS, headers=self.HEADERS, timeout=self.TIMEOUT)
            elif self.METHODS == 'PUT':Result = self.Session.put(self.URL, data=self.PARAMS, headers=self.HEADERS, timeout=self.TIMEOUT)
            else:
                if self.PARAMS is None:Result = self.Session.get(self.URL, headers=self.HEADERS, timeout=self.TIMEOUT)
                else:Result = self.Session.get(self.URL, params=self.PARAMS, headers=self.HEADERS, timeout=self.TIMEOUT)
            self.Session.close()
            
            try:return dict(json.loads(Result.text))
            except:return str(Result.text)
        except ProxyError as e:raise Error(f'ProxyError')
        except ConnectTimeout as e:raise Error(f'ConnectTimeout')
        except ConnectionError as e:raise Error(f'ConnectionError')
        except ReadTimeout as e:raise Error(f'ReadTimeout')
        except JSONDecodeError:raise Error(f'JSONDecodeError')
        except TooManyRedirects as e:raise Error(f'TooManyRedirects')
        except Exception as e:raise Exception(str(e))