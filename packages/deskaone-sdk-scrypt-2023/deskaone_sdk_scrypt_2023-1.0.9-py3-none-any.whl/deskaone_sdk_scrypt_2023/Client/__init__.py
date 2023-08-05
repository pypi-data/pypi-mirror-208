import json
from requests.auth import AuthBase
import time, base64, hmac, requests
from requests import Response
from typing import Optional
from deskaone_sdk_scrypt_2023.Exceptions import Error
from deskaone_sdk_scrypt_2023.Utils import Crypto, __version_code__
from deskaone_sdk_scrypt_2023.Internal import Internal

class __Auth__(AuthBase):
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp   = str(int(time.time() * 1000))
        message     = str(timestamp + request.method + request.path_url + (request.body or ''))
        signature   = base64.b64encode(hmac.new(self.secret_key.encode(), message.encode(), 'SHA256').digest()).decode()
        request.headers.update({
            'User-Agent'    : f'DesKaOne-Scrypt-SDK-2023@{__version_code__}',
            'SIGNATURE'     : signature,
            'TIMESTAMP'     : timestamp,
            'VERSION'       : __version_code__
        })
        return request

class Client:
    
    def __init__(self, *args, **kwargs) -> None:
        """A Internal Requests.
        
        Basic Usage::

            ClientV2(
                RPC_API     = str,
                SECRETKEY   = bool (Optional)
            )
            
        params 
        """
        self._RPC_API, self._secretKey = kwargs.get('RPC_API'), kwargs.get('SECRETKEY')
        if self._RPC_API is None:raise Error('RPC API Require')
        if self._secretKey is None:raise Error('SECRETKEY Require')
        self._CR = Crypto.AES()
        self._CR.randomIv()
        self._CR.randomKey()
        self.Session    = requests.Session()
    
    def __requests__(self, *args, **kwargs) -> dict:
        try:
            if type(kwargs.get('PARAMS')) == dict:
                self._CR.setData_FromString(json.dumps(kwargs.get('PARAMS'), separators=(',', ':')))
                DATA = f'{len(self._CR.getIv_to_Hex())}|{len(self._CR.getKey_to_Hex())}|{len(self._CR.encrypt_to_hex())}|{self._CR.getKey_to_Hex()}{self._CR.getIv_to_Hex()}{self._CR.encrypt_to_hex()}'
                PARAMS  = json.dumps(dict(DATA = DATA), separators=(',', ':'))
            else: raise Error(f'PARAMS dict not {type(kwargs.get("PARAMS"))}')
            if kwargs.get('APP') == 'Credits':URL = f'{self._RPC_API}/Secret'
            elif kwargs.get('APP') == 'getProxy':URL = f'{self._RPC_API}/getProxy'
            elif kwargs.get('APP') == 'addProxy':URL = f'{self._RPC_API}/addProxy'
            elif kwargs.get('APP') == 'getVersion':URL = f'{self._RPC_API}/getVersion'
            elif kwargs.get('APP') == 'getScrypt':URL = f'{self._RPC_API}/getScrypt'
            elif kwargs.get('APP') == 'Coinbase':URL = f'{self._RPC_API}/Coinbase'
            elif kwargs.get('APP') == 'Bprogrammers':URL = f'{self._RPC_API}/Bprogrammers'
            elif kwargs.get('APP') == 'PlayFabapi':URL = f'{self._RPC_API}/PlayFabapi'
            elif kwargs.get('APP') == 'Viker':URL = f'{self._RPC_API}/Viker'
            elif kwargs.get('APP') == 'Email':URL = f'{self._RPC_API}/Email'
            elif kwargs.get('APP') == 'AntiCaptcha':URL = f'{self._RPC_API}/AntiCaptcha'
            elif kwargs.get('APP') == 'Zebedee':URL = f'{self._RPC_API}/Zebedee'
            elif kwargs.get('APP') == 'Test':URL = f'{self._RPC_API}/Test'
            else:URL = f'{self._RPC_API}/{kwargs.get("APP")}'
            RESULT  = self.Session.post(URL, data=PARAMS, auth=__Auth__(self._secretKey))
            CODE    = RESULT.status_code
            SPLIT   = str(RESULT.text).split('|')
            self._CR.setKey_from_Hex(SPLIT[3][:int(SPLIT[1])])
            self._CR.setIv_from_Hex(SPLIT[3][int(SPLIT[1]):int(SPLIT[1]) + int(SPLIT[0])])
            self._CR.setData_FromHex(SPLIT[3][int(SPLIT[1]) + int(SPLIT[0]):])
            return self._CR.decrypt_to_dict()
        except Error as e:raise Error(str(e))
        except Exception as e:raise Exception(str(e))
    
    def setParams(self, COMMAND = 'EXTERNAL', TIMEOUT = 60, PROXY = False, IPPORT = None, TYPEIP = None, *args, **kwargs) -> dict:
        return dict(COMMAND = COMMAND, TIMEOUT = TIMEOUT, PROXY = PROXY, IPPORT = IPPORT, TYPEIP = TYPEIP, **kwargs)
    
    def setRequest(self, *args, **kwargs) -> dict:
        """A Internal Requests.
        
        Basic Usage::

            setRequest(
                APP     = str | Credits or getProxy or addProxy or getVersion or getScrypt or Coinbase or Bprogrammers or PlayFabapi or Viker or Email or AntiCaptcha or Other or Zebedee,
                PARAMS  = dict
            )
            
        params is 
        """
        try:
            REQUEST = self.__requests__(**kwargs)
            DATA    = REQUEST.get('DATA')
            if type(DATA) == dict:
                if DATA.get('COMMAND') == 'INTERNAL':
                    if DATA.get('PROXY') is True:IPPORT, TYPEIP = DATA.get('IPPORT'), DATA.get('TYPEIP')
                    else: IPPORT, TYPEIP = None, None
                    URL, PARAMS, HEADERS, TIMEOUT, METHODS = DATA.get('URL'), json.dumps(DATA.get('PARAMS'), separators=(',', ':')) if type(DATA.get('PARAMS')) == dict else DATA.get('PARAMS'), DATA.get('HEADERS'), 60 if DATA.get('TIMEOUT') is None else DATA.get('TIMEOUT'), DATA.get('METHODS')
                    Result = Internal(URL = URL, PARAMS = PARAMS, HEADERS = HEADERS).Setup(IPPORT = IPPORT, TYPEIP = TYPEIP, METHODS = METHODS, TIMEOUT = TIMEOUT)
                    RESULT = dict(STATUS = True, MESSAGE = REQUEST.get('MESSAGE'), DATA = dict(Result = Result, CustomData = DATA.get('CustomData')), IP = REQUEST.get('IP'))
                else: RESULT = REQUEST
            else: RESULT = REQUEST
            return RESULT
        except Error as e:return dict(STATUS = False, MESSAGE = str(e), DATA = dict(), IP = None)
        except Exception as e:return dict(STATUS = False, MESSAGE = str(e), DATA = dict(), IP = None)