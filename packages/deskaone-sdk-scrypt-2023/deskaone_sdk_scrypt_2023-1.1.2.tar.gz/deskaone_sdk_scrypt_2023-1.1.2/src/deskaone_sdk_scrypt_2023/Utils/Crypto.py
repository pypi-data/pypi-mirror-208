import json, hashlib, hmac, base64, base58
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from typing import Optional

class Crypto:
    
    class AES:
        
        MODE_ECB = 1        #: Electronic Code Book (:ref:`ecb_mode`)
        MODE_CBC = 2        #: Cipher-Block Chaining (:ref:`cbc_mode`)
        MODE_CFB = 3        #: Cipher Feedback (:ref:`cfb_mode`)
        MODE_OFB = 5        #: Output Feedback (:ref:`ofb_mode`)
        MODE_CTR = 6        #: Counter mode (:ref:`ctr_mode`)
        MODE_OPENPGP = 7    #: OpenPGP mode (:ref:`openpgp_mode`)
        MODE_CCM = 8        #: Counter with CBC-MAC (:ref:`ccm_mode`)
        MODE_EAX = 9        #: :ref:`eax_mode`
        MODE_SIV = 10       #: Galois Counter Mode (:ref:`gcm_mode`)
        MODE_GCM = 11       #: Synthetic Initialization Vector (:ref:`siv_mode`)
        MODE_OCB = 12       #: Offset Code Book (:ref:`ocb_mode`)
        
        IV_LENGTH = AES.block_size
        KEY_LENGTH = AES.block_size * 2
        
        def __init__(self, Key: Optional[str] = None, Iv: Optional[str] = None, Mode: Optional[int] = None) -> None: self.block_size, self.Key, self.Iv, self.Mode = AES.block_size, get_random_bytes(self.KEY_LENGTH) if Key is None else Key.encode(), get_random_bytes(self.IV_LENGTH) if Iv is None else Iv.encode(), AES.MODE_CBC if Mode is None else Mode
                
        def setKey_from_Bytes(self, Key: bytes): self.Key = Key
        def setKey_from_String(self, Key: str): self.Key = Key.encode()
        def setKey_from_Hex(self, Key: str): self.Key = bytes.fromhex(Key)
        def setKey_from_base64(self, Key: str): self.Key = base64.b64decode(Key)
        def setKey_from_base58(self, Key: str): self.Key = base58.b58decode(Key)
        
        def setIv_from_Bytes(self, Iv: bytes): self.Iv = Iv
        def setIv_from_String(self, Iv: str): self.Iv = Iv.encode()
        def setIv_from_Hex(self, Iv: str): self.Iv = bytes.fromhex(Iv)
        def setIv_from_base64(self, Iv: str): self.Iv = base64.b64decode(Iv)
        def setIv_from_base58(self, Iv: str): self.Iv = base58.b58decode(Iv)
                
        def randomKey(self): self.Key = get_random_bytes(self.KEY_LENGTH)
        def randomIv(self): self.Iv = get_random_bytes(self.IV_LENGTH)
                
        def getKey_to_String(self): return self.Key.decode()
        def getKey_to_Hex(self): return self.Key.hex()
        def getKey_to_base64(self): return base64.b64encode(self.Key).decode()
        def getKey_to_base58(self): return base58.b58encode(self.Key).decode()
        def getKey_to_bytes(self): return self.Key
                
        def getIv_to_String(self): return self.Iv.decode()
        def getIv_to_Hex(self): return self.Iv.hex()
        def getIv_to_base64(self): return base64.b64encode(self.Iv).decode()
        def getIv_to_base58(self): return base58.b58encode(self.Iv).decode()
        def getIv_to_bytes(self): return self.Iv
            
        def setData_FromString(self, Data: str): self.Data   = self.__pad__V1(Data)
        def setData_FromString_pad_V2(self, Data: str): self.Data   = self.__pad__V2(Data)
        def setData_FromBase64(self, Data: str): self.Data   = base64.b64decode(Data)
        def setData_FromBase58(self, Data: str): self.Data   = base58.b58decode(Data)
        def setData_FromHex(self, Data: str):self.Data   = bytes.fromhex(Data)
        def setData_FromBytes(self, Data: bytes):self.Data   = Data
            
        def setMode(self, Mode = 2):
            
            """A setMode Requests.
        
            Basic Usage::

                MODE_ECB = 1        #: Electronic Code Book (:ref:`ecb_mode`)
                MODE_CBC = 2        #: Cipher-Block Chaining (:ref:`cbc_mode`)
                MODE_CFB = 3        #: Cipher Feedback (:ref:`cfb_mode`)
                MODE_OFB = 5        #: Output Feedback (:ref:`ofb_mode`)
                MODE_CTR = 6        #: Counter mode (:ref:`ctr_mode`)
                MODE_OPENPGP = 7    #: OpenPGP mode (:ref:`openpgp_mode`)
                MODE_CCM = 8        #: Counter with CBC-MAC (:ref:`ccm_mode`)
                MODE_EAX = 9        #: :ref:`eax_mode`
                MODE_SIV = 10       #: Galois Counter Mode (:ref:`gcm_mode`)
                MODE_GCM = 11       #: Synthetic Initialization Vector (:ref:`siv_mode`)
                MODE_OCB = 12       #: Offset Code Book (:ref:`ocb_mode`)
                
            params is Json/urlencode for POST/PUT or urlencode for GET
            """
            self.Mode = AES.MODE_CBC if Mode is None else Mode
        
        @staticmethod
        def __pad__V1(string: str): return str(string + (AES.block_size - len(string) % AES.block_size) * chr(AES.block_size - len(string) % AES.block_size)).encode()
        @staticmethod
        def __pad__V2(string: str): return str(string + (AES.block_size - len(string) % AES.block_size) * chr(0)).encode()
        @staticmethod
        def __unpad__V1(string: str): return string[0:-ord(string[-1:])]
        @staticmethod
        def __unpad__V2(string: str) -> str: return ''.join([chr(s) if int(s) != 0 else '' for s in string])
            
        def encrypt_to_base64(self): return base64.b64encode(AES.new(self.Key, self.Mode).encrypt(self.Data)).decode() if self.Mode == self.MODE_ECB else base64.b64encode(AES.new(self.Key, self.Mode, self.Iv).encrypt(self.Data)).decode() 
        def encrypt_to_base58(self): return base58.b58encode(AES.new(self.Key, self.Mode).encrypt(self.Data)).decode() if self.Mode == self.MODE_ECB else base58.b58encode(AES.new(self.Key, self.Mode, self.Iv).encrypt(self.Data)).decode()
        def encrypt_to_hex(self): return AES.new(self.Key, self.Mode).encrypt(self.Data).hex() if self.Mode == self.MODE_ECB else AES.new(self.Key, self.Mode, self.Iv).encrypt(self.Data).hex()
        def encrypt_to_bytes(self): return AES.new(self.Key, self.Mode).encrypt(self.Data) if self.Mode == self.MODE_ECB else AES.new(self.Key, self.Mode, self.Iv).encrypt(self.Data)
        
        def decrypt_to_string(self): return self.__unpad__V1(AES.new(self.Key, self.Mode).decrypt(self.Data)).decode("utf-8") if self.Mode == self.MODE_ECB else self.__unpad__V1(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data)).decode("utf-8")
        def decrypt_to_dict(self): return dict(json.loads(self.__unpad__V1(AES.new(self.Key, self.Mode).decrypt(self.Data)).decode("utf-8"))) if self.Mode == self.MODE_ECB else dict(json.loads(self.__unpad__V1(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data)).decode("utf-8")))
        def decrypt_to_list(self): return list(json.loads(self.__unpad__V1(AES.new(self.Key, self.Mode).decrypt(self.Data)).decode("utf-8"))) if self.Mode == self.MODE_ECB else list(json.loads(self.__unpad__V1(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data)).decode("utf-8")))
        def decrypt_to_bytes(self): return self.__unpad__V1(AES.new(self.Key, self.Mode).decrypt(self.Data)) if self.Mode == self.MODE_ECB else self.__unpad__V1(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data))
        
        def decrypt_to_string__unpad_V2(self): return self.__unpad__V2(AES.new(self.Key, self.Mode).decrypt(self.Data)) if self.Mode == self.MODE_ECB else self.__unpad__V2(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data))
        def decrypt_to_dict__unpad_V2(self): return dict(json.loads(self.__unpad__V2(AES.new(self.Key, self.Mode).decrypt(self.Data)))) if self.Mode == self.MODE_ECB else dict(json.loads(self.__unpad__V2(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data))))
        def decrypt_to_list__unpad_V2(self): return list(json.loads(self.__unpad__V2(AES.new(self.Key, self.Mode).decrypt(self.Data)))) if self.Mode == self.MODE_ECB else list(json.loads(self.__unpad__V2(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data))))
        def decrypt_to_bytes__unpad_V2(self): return self.__unpad__V2(AES.new(self.Key, self.Mode).decrypt(self.Data)).encode() if self.Mode == self.MODE_ECB else self.__unpad__V2(AES.new(self.Key, self.Mode, self.Iv).decrypt(self.Data)).encode()
        
    class HMAC:
        
        @staticmethod
        def shake_256(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'shake_256')
        
        @staticmethod
        def shake_128(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'shake_128')
        
        @staticmethod
        def sha3_512(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha3_512')
        
        @staticmethod
        def sha3_384(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha3_384')
        
        @staticmethod
        def sha3_256(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha3_256')
        
        @staticmethod
        def sha3_224(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha3_224')
        
        @staticmethod
        def blake2s(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'blake2s')
        
        @staticmethod
        def blake2b(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'blake2b')
        
        @staticmethod
        def sha512(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha512')
        
        @staticmethod
        def sha384(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha384')
        
        @staticmethod
        def sha256(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha256')
        
        @staticmethod
        def sha224(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha224')
        
        @staticmethod
        def sha1(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'sha1')
        
        @staticmethod
        def md5(key: str, string: str): return hmac.new(key.encode(), string.encode(), 'md5')
        
    class HASHLIB:
        
        @staticmethod
        def shake_256(string: str): return hashlib.shake_256(string.encode())
        
        @staticmethod
        def shake_128(string: str): return hashlib.shake_128(string.encode())
        
        @staticmethod
        def sha3_512(string: str): return hashlib.sha3_512(string.encode())
        
        @staticmethod
        def sha3_384(string: str): return hashlib.sha3_384(string.encode())
        
        @staticmethod
        def sha3_256(string: str): return hashlib.sha3_256(string.encode())
        
        @staticmethod
        def sha3_224(string: str): return hashlib.sha3_224(string.encode())
        
        @staticmethod
        def blake2s(string: str): return hashlib.blake2s(string.encode())
        
        @staticmethod
        def blake2b(string: str): return hashlib.blake2b(string.encode())
        
        @staticmethod
        def sha512(string: str): return hashlib.sha512(string.encode())
        
        @staticmethod
        def sha384(string: str): return hashlib.sha384(string.encode())
        
        @staticmethod
        def sha256(string: str): return hashlib.sha256(string.encode())
        
        @staticmethod
        def sha224(string: str): return hashlib.sha224(string.encode())
        
        @staticmethod
        def sha1(string: str): return hashlib.sha1(string.encode())
        
        @staticmethod
        def md5(string: str): return hashlib.md5(string.encode())
        
    class DICT(dict): ...
        
    class LIST(list): ...
    