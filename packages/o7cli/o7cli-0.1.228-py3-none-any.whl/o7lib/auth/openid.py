
# Where to find Open Id configuration
# https://[base-server-url]/.well-known/openid-configuration
# example: https://accounts.google.com/.well-known/openid-configuration
# example: https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_vdyge4T9V/.well-known/openid-configuration


import os
import logging
import pprint
import uuid
import urllib

import jwt
import requests

logger = logging.getLogger(__name__)

# Key Pair of JWKS url for each known iss
urlJwksForIss = {}
urlConfigForIss = {}

#*************************************************
#
#*************************************************
class OpenIdError(Exception):
    pass
    #
    # def __init__(self, value):
    #     self.value = value
    # def __str__(self):
    #     return "Open Id Error: %s" % self.value


def MustExist(value, name):
    """ Raise exception if value is None """
    if value is None:
        raise OpenIdError(f'Environement varible {name} is required')

    return value

#*************************************************
#
#*************************************************
class OpenId():

    #*************************************************
    #
    #*************************************************
    def __init__(self, *,
        provider = None,
        clientId = None,
        clientSecret = None,
        callback = None,
        providerConfig=None,

        scope = 'openid',
        nonce = 'nonce'
    ):

        self.provider = MustExist(os.getenv('OIDC_PROVIDER', default=provider), 'OIDC_PROVIDER')
        self.clientId = MustExist(os.getenv('OIDC_CLIENT_ID', default=clientId), 'OIDC_CLIENT_ID')
        self.clientSecret = MustExist(os.getenv('OIDC_CLIENT_SECRET', default=clientSecret), 'OIDC_CLIENT_SECRET')
        self.callback = MustExist(os.getenv('OIDC_CALLBACK', default=callback), 'OIDC_CALLBACK')


        self.providerConfig = providerConfig
        if self.providerConfig is None:
            self.Discover()

        self.scope = scope
        self.nonce = nonce

        self.VerifyConfig()


    #*************************************************
    #  Ensure we have all required
    #*************************************************
    def VerifyConfig(self):

        if 'authorization_endpoint' not in self.providerConfig:
            raise OpenIdError('Provider Config is missing: authorization_endpoint')

        if 'token_endpoint' not in self.providerConfig:
            raise OpenIdError('Provider Config is missing: authorization_endpoint')


    #*************************************************
    #
    #*************************************************
    def Discover(self):
        """Get provider config from .well-known/openid-configuration"""

        url = f'https://{self.provider}/.well-known/openid-configuration'
        logger.info(f'discover: url -> {url}')

        response = requests.get(url=url, timeout=5)

        if response.status_code != 200 :
            logger.error(f'discover: Got Error Status Code: {response.status_code}')
            logger.error(f'discover: Error Message: {response.text}')
            raise OpenIdError('Discovery endpoint is not reponding')

        try :
            self.providerConfig = response.json()
        except requests.exceptions.JSONDecodeError as excp:
            logger.error(f'discover: Did not rx JSON format {response.text}')
            raise OpenIdError('Discovery endpoint is not reponding JSON') from excp


        print('discover Rx Info: ->')
        pprint.pprint(self.providerConfig)


    #*************************************************
    #
    #*************************************************
    def GetLoginUrl(self):
        """Get login url to return to client"""


        # Generate random cookie
        nonce = str(uuid.uuid4())
        logger.info(f'GetLoginUrl: {self.nonce}={nonce}')

        authEndpoint = self.providerConfig['authorization_endpoint']
        query = {
            'response_mode' : 'query',  # or form_post
            'response_type' : 'code', # or id_token
            'scope' : self.scope,
            'client_id' : self.clientId,
            'redirect_uri' : self.callback,
            self.nonce : nonce
        }

        queryStr = urllib.parse.urlencode(query)
        url = f'{authEndpoint}?{queryStr}'

        logger.info(f'GetLoginUrl: url={url}')

        return url, nonce

    #*************************************************
    #  Exchanges code for tokens using backend secured channel
    # Ref : https://auth0.com/docs/api/authentication#authorization-code-flow45
    #*************************************************
    def GetTokens(self, code):

        headers = {
            'content-type' : 'application/x-www-form-urlencoded',
            'accept' : 'application/json'
        }

        params = {
            'grant_type' : 'authorization_code',
            'client_id' : self.clientId,
            'client_secret' : self.clientSecret,
            'redirect_uri' : self.callback,
            'code' : code
        }

        auth = requests.auth.HTTPBasicAuth(self.clientId, self.clientSecret)

        print("TX headers -> ", headers)
        print("TX params -> ", params)
        req = requests.post(
            url=self.providerConfig['token_endpoint'],
            data=params,
            params=params,
            headers=headers,
            auth = auth
        )
        print("req.url -> ", req.url)
        print("req.headers -> ", req.headers)
        print("RX test -> ", req.text)

        if req.status_code != 200 :
            print(f'Got Error Status Code: {req.status_code}')
            print(f'Error Message: {req.text}')
            raise OpenIdError('Token endpoint error')

        tokens = req.json()
        print('<------ TOKENS ------------------->')
        pprint.pprint(tokens)
        print('<--------------------------------->')

        return tokens

    #*************************************************
    #  Validate Id Tokens and returns claims
    #*************************************************
    def validateIdToken(self, idToken, nonce):

        jwksClient = jwt.PyJWKClient(self.providerConfig['jwks_uri'])
        pubKey = jwksClient.get_signing_key_from_jwt(idToken)
        claims = jwt.decode(
            idToken,
            pubKey.key,
            algorithms=["RS256"],
            audience=self.clientId,
            issuer = self.providerConfig['issuer'],
            require = ['exp', 'iat', 'aud', 'iss'],
            verify_signature = True,
            verify_aud = True,
            verify_iss = True,
            verify_exp = True,
            verify_iat = True
        )

        print('<------ TOKEN CLAIMS ------------------->')
        pprint.pprint(claims)
        print('<--------------------------------->')

        # Verify nonce
        if claims['nonce'] != nonce: raise OpenIdError('Nonce is not matching')

        return claims


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    # Usage Example

    logging.basicConfig(level=logging.DEBUG)

    providerConfig = {
        "issuer":"https://oauth.platform.intuit.com/op/v1",
        "authorization_endpoint":"https://appcenter.intuit.com/connect/oauth2",
        "token_endpoint":"https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        "userinfo_endpoint":"https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo",
        "revocation_endpoint":"https://developer.api.intuit.com/v2/oauth2/tokens/revoke",
        "jwks_uri":"https://oauth.platform.intuit.com/op/v1/jwks",
        "response_types_supported":[
            "code"
        ],
        "subject_types_supported":[
            "public"
        ],
        "id_token_signing_alg_values_supported":[
            "RS256"
        ],
        "scopes_supported":[
            "openid",
            "email",
            "profile",
            "address",
            "phone"
        ],
        "token_endpoint_auth_methods_supported":[
            "client_secret_post",
            "client_secret_basic"
        ],
        "claims_supported":[
            "aud",
            "exp",
            "iat",
            "iss",
            "realmid",
            "sub"
        ]
    }

    obj = OpenId(
        provider = 'developer.api.intuit.com',
        clientId = 'ABFcnnQa19xtcvlBAc0mNurwsvxywjs8dtjAITTj2802vkhZlE',
        clientSecret= 'dh9TUUroFB57iYTYz6uIZp8xOeCUtNIQ0X5U6Pd8',
        callback = 'http://localhost:5000/callback',
        providerConfig=providerConfig
    )


#     obj.GetLoginUrl()

