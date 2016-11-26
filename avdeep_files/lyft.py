
import requests
import requests.auth


LyftCLientId = 'njKAAMEoDFge'
LyftClientSecret = 'oQf6gnjZLNKfugCqgVJIwF06rgbHpwpA'


# retrieving an access token
def RetreivePublicToken():
    datatosend = {
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    obj = requests.post('https://api.lyft.com/oauth/token', auth=requests.auth.HTTPBasicAuth(LyftCLientId, LyftClientSecret), json=datatosend)
    json = obj.json()
    print(json['access_token'])


# for user to give access to our app to access his account
def ObtainingAccessToUsersLyftAccount():
    access_info = requests.get('https://api.lyft.com/oauth/authorize', params={
        'client_id': 'njKAAMEoDFge',
        'response_type': 'code',
        'scope': 'public rides.read rides.request',
        'state' : 'payload'
    })

    print(access_info.url)

# getting access of users lyft account :
def GetAccessTokenReal(authorizationCode):
    data = {
        'grant_type': 'authorization_code',
        'code': authorizationCode
    }
    return requests.post('https://api.lyft.com/oauth/token', auth=requests.auth.HTTPBasicAuth(LyftCLientId, LyftClientSecret), json=data)


def RefreshToken():
    headers = {"Content-Type: application/json"}
    data = {
               "grant_type": "refresh_token",
    }
    return requests.post('https://api.lyft.com/oauth/token',auth =requests.auth.HTTPBasicAuth(LyftCLientId,LyftClientSecret),json=data,headers=headers)


b= RetreivePublicToken()
a = ObtainingAccessToUsersLyftAccount()
c= GetAccessTokenReal('K8e-sgC69BHV1fvf')
print(c.json())


a= requests.get('https://api.uber.com/v1/estimates/price?start_latitude=37.625732&start_longitude=-122.377807&end_latitude=37.785114&end_longitude=-122.406677&server_token=hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS')
print(a.json())


