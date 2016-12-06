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
    print (latlongdict)

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


def get_route_metrics(start_latitude, start_longitude,
                      end_latitude, end_longitude):
    auth_token = "gAAAAABYPhlbLHhENo0iMVhrcEVtaMed3UuZEe4-DQyqNE7I0gVLBmgK1zM7No3gQHdznH3P8ybTbIssHeUZvjiz0lFsHipzwYdKpqyo2J_HBwCnXJmBZ2KauWjaFLwVG7979hKgni8U8p1N5dob8mExoxPoZVXIHNnP1Z2wlZDOuonyizDK0Es_2r8c3KAM7i_8xtx1b0O97Tkn0jMUVJLsfpUDLx3f2w=="


    query = "https://api.lyft.com/v1/cost?"

    # Construct GET query parameters.
    query += "&start_lat=" + str(start_latitude)
    query += "&start_lng=" + str(start_longitude)
    query += "&end_lat=" + str(end_latitude)
    query += "&end_lng=" + str(end_longitude)

    response = requests.get(query, headers={'Authorization': 'Bearer ' + str(auth_token)})

    price_map = {}
    for packet in response.json()['cost_estimates']:
        # TODO: handle the case when no costs are returned, return appropriate errors.
        price_map[packet['display_name']] = \
            {'low_price_dollars': packet['estimated_cost_cents_min'] / 100,
             'high_price_dollars': packet['estimated_cost_cents_max'] / 100,
             'multiplier': 1 + float(packet['primetime_percentage'][:-1]) / 100.0,
             'duration_sec': packet['estimated_duration_seconds']}
    print(price_map)




# p= get_route_metrics(37.3310001,-121.860433,37.335369,-121.876073)



accesstoken= RetreivePublicToken()
# a = ObtainingAccessToUsersLyftAccount()
# c= GetAccessTokenReal('K8e-sgC69BHV1fvf')
# print(c.json())


# a= requests.get('https://api.uber.com/v1/estimates/price?start_latitude=37.625732&start_longitude=-122.377807&end_latitude=37.785114&end_longitude=-122.406677&server_token=hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS')
# print(a.json())
# srcloc = 'Walmart Supercenter, 777 Story Rd, San Jose, CA 95122'
# dstdoc = '351 S 11th St, San Jose, CA 95112'
# a = COST_DEPENDING_ON_RIDE_TYPE(srcloc, dstdoc)
#
# b = GETCOST(srcloc,dstdoc)