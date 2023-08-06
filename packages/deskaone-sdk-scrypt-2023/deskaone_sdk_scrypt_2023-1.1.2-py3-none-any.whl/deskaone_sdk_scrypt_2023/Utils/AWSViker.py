import hmac
import hashlib
import datetime
from urllib.parse import quote, urlparse

class AWSViker:
    
    def __init__(self,
                 aws_access_key,
                 aws_secret_access_key,                 
                 aws_region,
                 aws_service,
                 aws_token,
                 aws_api_version,
                 aws_user_agent,
                 content_type):
        """
        Example usage for talking to an AWS Elasticsearch Service:

        AWSRequestsAuth(aws_access_key='YOURKEY',
                        aws_secret_access_key='YOURSECRET',
                        aws_host='search-service-foobar.us-east-1.es.amazonaws.com',
                        aws_region='us-east-1',
                        aws_service='es',
                        aws_token='...')

        The aws_token is optional and is used only if you are using STS
        temporary credentials.
        """
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        self.service = aws_service
        self.aws_token = aws_token
        self.aws_api_version = aws_api_version
        self.aws_user_agent = aws_user_agent
        self.content_type = content_type
    
    def sign(self, key: bytes, msg: str):
        """
        Copied from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
        """
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


    def getSignatureKey(self, key: str, dateStamp: str, regionName: str, serviceName: str):
        """
        Copied from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
        """
        kDate = self.sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = self.sign(kDate, regionName)
        kService = self.sign(kRegion, serviceName)
        kSigning = self.sign(kService, 'aws4_request')
        return kSigning
    
    #def get_aws_request_headers(self, url: str, payload: str, method: str):
    def get_aws_request_headers(self, URL: str, PAYLOAD: str, METHOD: str):
        """
        Returns a dictionary containing the necessary headers for Amazon's
        signature version 4 signing process. An example return value might
        look like

            {
                'Authorization': 'AWS4-HMAC-SHA256 Credential=YOURKEY/20160618/us-east-1/es/aws4_request, '
                                 'SignedHeaders=host;x-amz-date, '
                                 'Signature=ca0a856286efce2a4bd96a978ca6c8966057e53184776c0685169d08abd74739',
                'x-amz-date': '20160618T220405Z',
            }
        """
        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')  # Date w/o time for credential_scope

        #amzdate     = '20230320T085753Z'
        #datestamp   = '20230320'
        
        canonical_uri = self.get_canonical_path(URL)

        canonical_querystring = self.get_canonical_querystring(URL)
        
        payload_hash = hashlib.sha256(PAYLOAD.encode()).hexdigest()

        # Create the canonical headers and signed headers. Header names
        # and value must be trimmed and lowercase, and sorted in ASCII order.
        # Note that there is a trailing \n.
        canonical_headers = (
            'content-length:' + str(len(PAYLOAD)) + '\n' + 'content-type:' + self.content_type + '\n' + 'host:' + urlparse(URL).hostname + '\n' + 'x-amz-api-version:' + self.aws_api_version + '\n' + 'x-amz-content-sha256:' + payload_hash + '\n' + 'x-amz-date:' + amzdate + '\n' + 'x-amz-security-token:' + self.aws_token + '\n' + 'x-amz-user-agent:' + self.aws_user_agent + '\n'
        )
        
        
        signed_headers = 'content-length;content-type;host;x-amz-api-version;x-amz-content-sha256;x-amz-date;x-amz-security-token;x-amz-user-agent'        

        # Combine elements to create create canonical request
        canonical_request = (METHOD + '\n' + canonical_uri + '\n' +
                             canonical_querystring + '\n' + canonical_headers +
                             '\n' + signed_headers + '\n' + payload_hash)
        #print(canonical_request)
        # Match the algorithm to the hashing algorithm you use, either SHA-1 or
        # SHA-256 (recommended)
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = (datestamp + '/' + self.aws_region + '/' +
                            self.service + '/' + 'aws4_request')
        string_to_sign = (algorithm + '\n' + amzdate + '\n' + credential_scope +
                          '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())

        # Create the signing key using the function defined above.
        signing_key = self.getSignatureKey(self.aws_secret_access_key,
                                      datestamp,
                                      self.aws_region,
                                      self.service)

        # Sign the string_to_sign using the signing_key
        string_to_sign_utf8 = string_to_sign.encode('utf-8')
        signature = hmac.new(signing_key,
                             string_to_sign_utf8,
                             hashlib.sha256).hexdigest()

        # The signing information can be either in a query string value or in
        # a header named Authorization. This code shows how to use a header.
        # Create authorization header and add to request headers
        authorization_header = (algorithm + ' ' + 'Credential=' + self.aws_access_key +
                                '/' + credential_scope + ', ' + 'SignedHeaders=' +
                                signed_headers + ', ' + 'Signature=' + signature)
        return {
                'Host' : urlparse(URL).hostname,
                'User-Agent' : 'UnityPlayer/2020.3.37f1 (UnityWebRequest/1.0, libcurl/7.80.0-DEV)',
                'Accept' : '*/*',
                'Accept-Encoding' : 'deflate, gzip',
                'Content-Type' : self.content_type,
                'x-amz-api-version' : self.aws_api_version,
                'x-amz-user-agent' : self.aws_user_agent,
                'X-amz-Security-Token' : self.aws_token,
                'X-Amz-Date' : amzdate,
                'X-Amz-Content-SHA256' : payload_hash,
                'Authorization' : authorization_header,
                'X-Unity-Version' : '2020.3.37f1',
                'Content-Length' : str(len(PAYLOAD))
            }
    
    def get_canonical_path(self, url: str):
        """
        Create canonical URI--the part of the URI from domain to query
        string (use '/' if no path)
        """
        parsedurl = urlparse(url)

        # safe chars adapted from boto's use of urllib.parse.quote
        # https://github.com/boto/boto/blob/d9e5cfe900e1a58717e393c76a6e3580305f217a/boto/auth.py#L393
        return quote(parsedurl.path if parsedurl.path else '/', safe='/-_.~')
    
    def get_canonical_querystring(self, url: str):
        """
        Create the canonical query string. According to AWS, by the
        end of this function our query string values must
        be URL-encoded (space=%20) and the parameters must be sorted
        by name.

        This method assumes that the query params in `r` are *already*
        url encoded.  If they are not url encoded by the time they make
        it to this function, AWS may complain that the signature for your
        request is incorrect.

        It appears elasticsearc-py url encodes query paramaters on its own:
            https://github.com/elastic/elasticsearch-py/blob/5dfd6985e5d32ea353d2b37d01c2521b2089ac2b/elasticsearch/connection/http_requests.py#L64

        If you are using a different client than elasticsearch-py, it
        will be your responsibility to urleconde your query params before
        this method is called.
        """
        canonical_querystring = ''

        parsedurl = urlparse(url)
        querystring_sorted = '&'.join(sorted(parsedurl.query.split('&')))

        for query_param in querystring_sorted.split('&'):
            key_val_split = query_param.split('=', 1)

            key = key_val_split[0]
            if len(key_val_split) > 1:
                val = key_val_split[1]
            else:
                val = ''

            if key:
                if canonical_querystring:
                    canonical_querystring += "&"
                canonical_querystring += u'='.join([key, val])

        return canonical_querystring