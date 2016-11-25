''' this program will
1.create a database and corresponding table
2.parse an address to get its attributes and put in the database
3.retrieve the data stored in the database '''

import MySQLdb
import geocoder
import json
from getlocationinfo import *


print  lat1
#connnect to your local database
#or your rds database
try:

    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="root",  # your username
                         passwd="********",
                         db="CMPE273")  # your password

except MySQLdb.OperationalError:
    print("connection failed")
#create a cursor to access your data

cur = db.cursor()


#create table if not exists for HOME ADDRESS
try:
    cur.execute("create table locationinfo(id INT NOT NULL AUTO_INCREMENT, lat FLOAT(20,15) NOT NULL, lng FLOAT(20,15) NOT NULL, street VARCHAR(255) NOT NULL, city VARCHAR(255) NOT NULL, state VARCHAR(255) NOT NULL,country VARCHAR(255) NOT NULL,postal BIGINT NOT NULL,neighborhood VARCHAR(255) NOT NULL, county VARCHAR(255)  NOT NULL, primary key(id))")
    print("Table created ")
except MySQLdb.OperationalError as e:
    print(e)

#create table if not exists for destination ADDRESS
try:
    cur.execute("create table locationinfodestination(id INT NOT NULL AUTO_INCREMENT, lat FLOAT(20,15) NOT NULL, lng FLOAT(20,15) NOT NULL, street VARCHAR(255) NOT NULL, city VARCHAR(255) NOT NULL, state VARCHAR(255) NOT NULL,country VARCHAR(255) NOT NULL,postal BIGINT NOT NULL,neighborhood VARCHAR(255) NOT NULL, county VARCHAR(255)  NOT NULL, primary key(id))")
    print("Table created ")
except MySQLdb.OperationalError as e:
    print(e)

#insert data into HOME
try:
    cur.execute("INSERT INTO locationinfo (lat,lng,street,city,state,country,postal,neighborhood,county) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)" , (lat,long,street,city,state,country,postaladdr,neighborhood,county))
    db.commit()
    print("Data inserted")
except MySQLdb.OperationalError as e:
    print(e)

#insert data into destination

try:
    cur.execute("INSERT INTO locationinfodestination (lat,lng,street,city,state,country,postal,neighborhood,county) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)" , (lat1,long1,street1,city1,state1,country1,postaladdr1,neighborhood1,county1))
    db.commit()
    print("Data inserted")
except MySQLdb.OperationalError as e:
    print(e)


#retrieve data from it
try:
    cur.execute("select * from locationinfo")

except MySQLdb.OperationalError:
    print("error")
print ("home")
for row in cur.fetchall():

    print row
try:
    cur.execute("select * from locationinfodestination")

except MySQLdb.OperationalError:
    print("error")

print ("DESTINATION")

for row in cur.fetchall():
    print row




db.close()




