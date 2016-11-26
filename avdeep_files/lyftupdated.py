import json

import requests
import requests.auth
import googlemaps



LyftCLientId = 'njKAAMEoDFge'
LyftClientSecret = 'oQf6gnjZLNKfugCqgVJIwF06rgbHpwpA'


def getLatLong(location):
    data = googlemaps.Client(key='AIzaSyDjgTKyC61SRs1p1rCISNK65PVflaHnC94')
    result = data.geocode(location)[0]
    latlongdict = result['geometry']['location']

    return latlongdict


# retrieving an access token
def RetreivePublicToken():
    datatosend = {
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    obj = requests.post('https://api.lyft.com/oauth/token', auth=requests.auth.HTTPBasicAuth(LyftCLientId, LyftClientSecret), json=datatosend)
    json = obj.json()
    print(json['access_token'])
    return json['access_token']


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



#get the response by sending a get request and the response we get contains all the information like {"cost_estimates": [{"ride_type": "lyft_plus", "estimated_duration_seconds": 411, "estimated_distance_miles": 1.64, "estimated_cost_cents_max": 2070, "primetime_percentage": "100%", "is_valid_estimate": true, "currency": "USD", "estimated_cost_cents_min": 1270, "display_name": "Lyft Plus", "primetime_confirmation_token": null, "can_request_ride": true}]}
def GETCOST(sourcelocation, destinationlocation):

    accesstoken = RetreivePublicToken()
    src_loc = getLatLong(sourcelocation)
    des_loc = getLatLong(destinationlocation)

    return requests.get('https://api.lyft.com/v1/cost', headers={
        'Authorization': 'Bearer ' + accesstoken
    }, params={
        'start_lat': src_loc['lat'],
        'start_lng':src_loc['lng'] ,
        'end_lat': des_loc['lat'],
        'end_lng': des_loc['lng']
    })



def COST_DEPENDING_ON_RIDE_TYPE(sourcelocation, destinationlocation):
    dictionary = GETCOST(sourcelocation,destinationlocation)
    print (type(dictionary.content))
    content_in_string = dictionary.content   #getting all the content in string so need ot convert it into json
    print (content_in_string)
    d = json.loads(content_in_string)  # converting all the content to json
    p= d['cost_estimates']
    #parsing through all the content we got and getting cost of rides corresponding to ride_type
    for i in range(len(p)):
        if(p[i]['ride_type'] == "lyft_plus"):
            mincost = p[i]['estimated_cost_cents_min']
            maxcost = p[i]['estimated_cost_cents_max']
            print ("lyft_plus minimum cost :",mincost , "cents")      # printing for testing purpose we can return a dict for the real use purpose
            print ("lyft_plus maximim cost :",maxcost , "cents")

        elif(p[i]['ride_type'] == "lyft_line"):
            mincost = p[i]['estimated_cost_cents_min']
            maxcost = p[i]['estimated_cost_cents_max']
            print ("lyft_line minimum cost :",mincost,"cents")
            print ("lyft_line maximum cost:",maxcost,"cents")

        elif(p[i]['ride_type'] == "lyft"):
            maxcost = p[i]['estimated_cost_cents_max']
            mincost = p[i]['estimated_cost_cents_min']
            print ("lyft minimum cost :",mincost,"cents")
            print ("lyft maximum cost:",maxcost,"cents")








accesstoken= RetreivePublicToken()
a = ObtainingAccessToUsersLyftAccount()
# c= GetAccessTokenReal('K8e-sgC69BHV1fvf')
# print(c.json())


# a= requests.get('https://api.uber.com/v1/estimates/price?start_latitude=37.625732&start_longitude=-122.377807&end_latitude=37.785114&end_longitude=-122.406677&server_token=hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS')
# print(a.json())
srcloc = 'Walmart Supercenter, 777 Story Rd, San Jose, CA 95122'
dstdoc = '351 S 11th St, San Jose, CA 95112'
a = COST_DEPENDING_ON_RIDE_TYPE(srcloc, dstdoc)

