import MySQLdb
import googlemaps


db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="root",  # your password
                     db="peepa")
cur = db.cursor()
latlongdict = {}
data = googlemaps.Client(key='AIzaSyDjgTKyC61SRs1p1rCISNK65PVflaHnC94')

result = data.geocode('351 S 11th St, San Jose, CA 95112')[0]

latlongdict =  result['geometry']['location']

latitude = latlongdict['lat']
longitude = latlongdict['lng']



cur.execute("insert into googlemap values(37.335369,-121.876073)")
db.commit()

cur.execute("SELECT * FROM googlemap")
for row in cur.fetchall():
    print (row[1])
    print (row[0])

db.close()
