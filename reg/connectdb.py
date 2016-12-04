import MySQLdb
import sys
import json
import geocoder


class Mysql(object):
    host = None
    user = None
    password = None
    database = None
    cursor = None
    db = None

    print "\n###################################"

    def __init__(self, host='localhost', user='root', password='Purgna11012', database='CMPE273'): #enter the password of you mysql
        self.host = host
        self.user = user
        self.password = password
        self.database = database


    #Open connection with database
    def open(self):
        try:
            print 'Checking MySQL connection...'

            self.db = MySQLdb.connect(self.host, self.user, self.password, self.database)

            self.cursor = self.db.cursor()
            print 'Connection OK, proceeding.'
        except MySQLdb.Error as error:
            print  error
            sys.exit()


    def close(self):
        self.cursor.close()
        self.db.close()
        print 'Connection closed!!!'
        print "\n###################################"

    def insert(self, table, *args, **kwargs):
        try:
            values = None
            query = "INSERT INTO %s " % table
            if kwargs:
                keys = kwargs.keys()
                values = kwargs.values()
                query += "(" + ",".join(["`%s`"]*len(keys)) % tuple(keys) + ") VALUES(" + ",".join(["%s"]*len(values)) + ")"
            elif args:
                values = args
                query +="VALUES(" + ",".join(["%s"]*len(values)) + ")"
            self.open()
            self.cursor.execute(query, values)
            self.db.commit()
            print 'Data inserted'
            self.close()
        except MySQLdb.Error as error:
            print  error
            print 'Data NOT inserted'
            self.close()


    def select(self, table, where=None, *args, **kwargs):
        try:
            query = 'SELECT '
            # keys
            keys = args
            values = tuple(kwargs.values())
            l = len(keys) - 1

            for i, key in enumerate(keys):
                query += "`" + key + "`"
                if i < l:
                    query += ","
            query += 'FROM %s' % table
            # where
            if where:
                query += " WHERE %s" % where


            self.open()
            self.cursor.execute(query, values)
            for row in self.cursor.fetchall():
                return row
            print 'Data selected'
            self.close()

        except MySQLdb.Error as error:
            print  error
            print 'Data not selected'
            self.close()



    def update(self, table, index, **kwargs):
        try:
            query = "UPDATE %s SET" % table
            keys = kwargs.keys()
            values = kwargs.values()
            l = len(keys) - 1
            for i, key in enumerate(keys):
                query += "`"+key+"`=%s"
                if i < l:
                    query += ","
            query += " WHERE User_id=%d" % index
            self.open()
            self.cursor.execute(query, values)
            self.db.commit()
            print 'Table Updated'
            self.close()

        except MySQLdb.Error as error:
            print  error
            print 'Table NOT Updated'
            self.close()


    def delete(self, table, index):
        try:
            query = "DELETE FROM %s WHERE User_id=%d" % (table, index)
            self.open()
            self.cursor.execute(query)
            self.db.commit()
            print 'Deleted Successful'
            self.close()
        except MySQLdb.Error as error:
            print  error
            print 'Deleted Failed'
            self.close()

def getlocationinfo(sourceaddr,login_id): # we need to provide the source address and the Login_id of the user to to save data
    g = geocoder.google(sourceaddr)
    a = g.geojson
    json_data = json.dumps(a)
    j = json.loads(json_data)
    lat = (j['geometry']['coordinates'][0])
    long = (j['geometry']['coordinates'][1])
    city = str(g.city)
    state = str(g.state)
    postaladdr = int(g.postal)
    mysql3=Mysql()
    forkey = mysql3.select('user_table', 'Login_id = %s ', 'User_id', Login_id=login_id)

    mysql3.insert("user_location_table",User_id=forkey,location_tag='N',address=sourceaddr,city=city,state=state,zipcode=postaladdr,latitude=lat,longitude=long)

Mysql2=Mysql()





