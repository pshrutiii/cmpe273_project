import json
import geocoder
#===========================================HOME INFO========================================

# get the json whic include all the info about a particular address
g = geocoder.google('32 sant avenue amritsar') # sanisha here you wiil provide the address of HOme
a = g.geojson

#parse that json
json_data = json.dumps(a)
j = json.loads(json_data)
coordinates = j['geometry']['coordinates']
lat = (j['geometry']['coordinates'][0])
long = (j['geometry']['coordinates'][1])
street =str(j['properties']['street'])
city = str(g.city)
state = str(g.state)
country = str(g.country)
postaladdr = int(g.postal)
neighborhood = str(j['properties']['neighborhood'])
county = str(j['properties']['county'])





#===========================================DESTINATION INFO========================================
# get the json whic include all the info about a particular address


# get the json whic include all the info about a particular address
g = geocoder.google('351 s 11 th street san jose') # sanisha here you wiil provide the address of DESTINATION
a = g.geojson

#parse that json
json_data = json.dumps(a)
j = json.loads(json_data)
coordinates1 = j['geometry']['coordinates']
lat1 = (j['geometry']['coordinates'][0])
long1 = (j['geometry']['coordinates'][1])
street1 =str(j['properties']['street'])
city1 = str(g.city)
state1 = str(g.state)
country1 = str(g.country)
postaladdr1 = int(g.postal)
neighborhood1 = str(j['properties']['neighborhood'])
county1 = str(j['properties']['county'])