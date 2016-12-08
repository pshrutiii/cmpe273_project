import MySQLdb
import gc
import threading

from connectdb import *
from cost_calculator import LyftCalculator, UberCalculator
from direction_finder import find_direction
from flask import render_template,redirect,request,url_for,g, session,flash
from flask import Flask
from multiprocessing.dummy import Pool as ThreadPool 
from passlib.hash import sha256_crypt
from wtforms import Form,TextField,PasswordField,validators

app = Flask(__name__)

db = MySQLdb.connect(host="localhost",  # host
                     user="root",  # username
                     passwd="root",  # password
                     db="CMPE273")  # db name
cur = db.cursor()

result1cost = 0.0
result2cost = 0.0
Index_Min_Cost = 0

###################################
DB_USER_TABLE = "user_table"

# Google API key.
MAPS_KEY = 'AIzaSyCs7YDHV5QF2QgJt8aJ1cKvFfxrIwSjsN0'
JS_API_KEY = 'AIzaSyBYXFWRwOAPQ03YrXRDfLheFkeV2nc0sAk'
###################################

@app.route('/addtag')
# def add_tag():
#       a = request.args.get('a', 0, type=str)
#       l = request.args.get('l', 0, type=str)
#       print "Added " + a + " -->> " + l
#       Mysql2 = Mysql()
#       Mysql2.insert('Tags', User_id=1, TAGaddress=a, TAGname=l)
#       return "nothing"
def add_tag():
    a = request.args.get('a', 0, type=str)  # COPY THIS
    l = request.args.get('l', 0, type=str)
    username = session['user']
    query_results = \
        cur.execute("SELECT * from user_table WHERE Login_id = '%s' " % (username))
    user_table_row = list(cur.fetchall())[0]
    print "Added " + a + " -->> " + l + "to DB for user_id = " + str(user_table_row[0])
    Mysql2 = Mysql()
    Mysql2.insert('Tags', User_id=user_table_row[0], TAGaddress=a, TAGname=l)
    return "nothing"

@app.route("/", methods =['GET', 'POST'])
def price_comparator():
    if g.user:
        try:
            # global JS_API_KEY
            # username = session['user']
            # query_results = \
            #         cur.execute("SELECT * from user_table WHERE Login_id = '%s' " % (username))
            # user_table_row = list(cur.fetchall())[0]
            #
            # tag_selection_query = \
            #         "SELECT * from Tags WHERE user_id = '%s'" % str(user_table_row[0])
            # print tag_selection_query
            # cur.execute(tag_selection_query)
            # allRows = {}
            # for row in cur.fetchall():
            #     print row[3] + " ---->>> " + row[2]
            #     allRows[row[3]] = row[2]  # adding to dictionary
            # dictVal = json.dumps(allRows)
            # print "Dict val is " + str(dictVal)
            # dictVal = {}
            # return render_template('price_comparator.html', maps_key=JS_API_KEY, row=dictVal)
            global JS_API_KEY  # COPY THIS
            username = session['user']
            query_results = \
                cur.execute("SELECT * from user_table WHERE Login_id = '%s' " % (username))
            user_table_row = list(cur.fetchall())[0]

            tag_selection_query = \
                "SELECT * from Tags WHERE user_id = '%s'" % str(user_table_row[0])
            # print tag_selection_query
            cur.execute(tag_selection_query)
            allRows = {}
            for row in cur.fetchall():
                # print row[3] + " -->>> " + row[2]
                allRows[row[3]] = row[2]  # adding to dictionary
            dictVal = json.dumps(allRows)
            print "Dict val is " + str(dictVal)
            return render_template('price_comparator.html', maps_key=JS_API_KEY, row=dictVal)
        except:
            flash("System Error.")
    else:
        flash("YOU NEED TO LOGIN")
        return redirect(url_for('login_page'))


@app.route('/logout',methods = ["POST"])
def logout():
    session.pop('user',None)
    print "session deleted"
    flash("YOU ARE LOGGED OUT")
    return render_template("login.html")



@app.route('/login', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']

            db = Mysql()
            login_id_selected = \
                Mysql2.select('user_table', 'login_id = %s ',
                        'login_id', login_id=attempted_username)

            if login_id_selected is None:
                flash("Username Does not exist.")
            else:
                selected_password = \
                    Mysql2.select('user_table', 'login_id = %s ',
                            'password', login_id=login_id_selected[0])

                if attempted_username == login_id_selected[0] and \
                    sha256_crypt.verify(attempted_password, selected_password[0]):
                    session['user'] = request.form['username']
                    return redirect(url_for('price_comparator'))
                else:
                    flash("Invalid Password. Try Again.")
        return render_template("login.html", error=error)
    except Exception:
        return render_template("login.html", error=error)

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            password = sha256_crypt.encrypt((str(form.password.data)))


            Mysql2 = Mysql()
            x = Mysql2.select('user_table', 'login_id = %s ', 'password', login_id=username)

            try:
                if int(len(x)) > 0:
                    flash("username already taken")
            except:
                 if(Mysql2.insert("user_table", login_id=username, password=password)):
                    gc.collect()
                 
                 session['user']=username
                 return render_template("price_comparator.html", form=form )

        return render_template("register.html", form=form )

    except Exception as e:
        return (str(e))

##############################################################################
def get_route_metrics(args):
    return args[0].get_route_metrics(*args[1:])

def get_trip_stats_summary(lyft_list, uber_list):
    results = {}
    combined_list = []
    for i in range(len(uber_list)):
      lyft_route_metrics = lyft_list[i]
      uber_route_metrics = uber_list[i]
      combined_route_metrics = lyft_route_metrics.copy()
      combined_route_metrics.update(uber_route_metrics)
      combined_list.append(combined_route_metrics)

    for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
        values = {'name': company.capitalize()}
        cost = 0
        total_time = 0

        for i in range(len(combined_list)):
            cost += combined_list[i][company]['low_price_dollars'] * combined_list[i][company]['multiplier']
            values['cost'] = round(cost, 2)
            total_time += combined_list[i][company]['duration_sec'] / 60.0
            values['total_time'] = round(total_time, 1)
            results[company] = values
    return results

def calculate_min_price_metrics(lyft, uber, waypoints, origin_lat, origin_lng,
        destination_lat, destination_lng):
    all_way_points_in_list = waypoints.split('|')

    if (len(all_way_points_in_list) == 2):
       waypoint1 = all_way_points_in_list[0]
       waypoint1 = waypoint1.split(',')
       waypoint1_lat = waypoint1[0]
       waypoint1_lng = waypoint1[1]

       waypoint2 = all_way_points_in_list[1]
       waypoint2 = waypoint2.split(',')
       waypoint2_lat = waypoint2[0]
       waypoint2_lng = waypoint2[1]

    elif (len(all_way_points_in_list) == 3):
       waypoint1 = all_way_points_in_list[0]
       waypoint1 = waypoint1.split(',')
       waypoint1_lat = waypoint1[0]
       waypoint1_lng = waypoint1[1]

       waypoint2 = all_way_points_in_list[1]
       waypoint2 = waypoint2.split(',')
       waypoint2_lat = waypoint2[0]
       waypoint2_lng = waypoint2[1]

       waypoint3 = all_way_points_in_list[2]
       waypoint3 = waypoint3.split(',')
       waypoint3_lat = waypoint3[0]
       waypoint3_lng = waypoint3[1]

    # 2 waypoints
    if (len(all_way_points_in_list) == 2):
        thread_pool = ThreadPool(6)
        
        # origin -> waypoint1 -> waypoint2 -> destination
        result1 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)])
        
        result1 = get_trip_stats_summary(price_list[0:3], price_list[3:6])
        print("Result1 : ", result1)

        #origin -> waypoint2 -> waypoint1 -> destination
        result2 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)])
        
        result2 = get_trip_stats_summary(price_list[0:3], price_list[3:6])
        print("Result2 : ", result2)

    # 3 way points
    if (len(all_way_points_in_list) == 3):
        thread_pool = ThreadPool(8)

        # origin -> waypoint1 -> waypoint2 -> waypoint3 -> destination
        result1 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)])
        result1 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result1 : ", result1)

        # origin -> waypoint1 -> waypoint3 -> waypoint2 -> destination
        result2 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)])
        result2 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result2 : ", result2)

        # origin -> waypoint2 -> waypoint1 -> waypoint3 -> destination
        result3 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)])
        result3 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result3 : ", result3)

        # origin -> waypoint2 -> waypoint3 -> waypoint1 -> destination
        result4 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)])
        result4 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result4 : ", result4)

        # origin -> waypoint3 -> waypoint2 -> waypoint1 -> destination
        result5 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)])
        result5 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result5 : ", result5)

        # origin -> waypoint3 -> waypoint1 -> waypoint2 -> destination
        result6 = {}
        price_list = thread_pool.map(get_route_metrics, 
                [(lyft, origin_lat, origin_lng, waypoint3_lat, waypoint3_lng),
                 (lyft, waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng),
                 (lyft, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (lyft, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng),
                 (uber, origin_lat, origin_lng, waypoint3_lat, waypoint3_lng),
                 (uber, waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng),
                 (uber, waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng),
                 (uber, waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)])
        result6 = get_trip_stats_summary(price_list[0:4], price_list[4:8])
        print("Result6 : ", result6)

    if(len(all_way_points_in_list) == 2):
        global result1cost
        result1cost = result1['Lyft Plus']['cost']
        global result2cost
        result2cost = result2['Lyft Plus']['cost']

        if result1cost < result2cost:
            final_result_metrics = result1
        else:
            final_result_metrics = result2

    elif(len(all_way_points_in_list) == 3):
        results = [result1['Lyft Plus']['cost'], 
                   result2['Lyft Plus']['cost'],
                   result3['Lyft Plus']['cost'],
                   result4['Lyft Plus']['cost'],
                   result5['Lyft Plus']['cost'],
                   result6['Lyft Plus']['cost']]
        global Index_Min_Cost
        Index_Min_Cost = results.index(min(results))
        final_result_metrics = eval("result" + str(1 + results.index(min(results))))
    return final_result_metrics

@app.route("/trips")
def trips():
  if g.user:
      origin = request.args['origin']
      origin_lat_long_list= origin.split(',')
      origin_lat =  origin_lat_long_list[0]
      origin_lng =  origin_lat_long_list[1]

      destination = request.args['destination']
      destination_lat_long_list= destination.split(',')
      destination_lat = destination_lat_long_list[0]
      destination_lng = destination_lat_long_list[1]

      waypoints = request.args['waypoints']
      all_way_points_in_list = waypoints.split('|')
      # print "DONNNNNNNNN : ",all_way_points_in_list

      formatted_addresses = request.args['formatted_addresses'].split("__||__")
      # print len(formatted_addresses)

      lyft = LyftCalculator()
      uber = UberCalculator()
      result_metrics = {}
      #####################################################################################
      waypoint_count = len(waypoints.split("|"))
      calculated_route = find_direction(MAPS_KEY, origin, destination, waypoints).json()

      if request.args['price_mode'] == "minprice" and waypoint_count > 1:
        result_metrics = \
            calculate_min_price_metrics(lyft, uber, waypoints, origin_lat,
                        origin_lng, destination_lat, destination_lng)
        minprice_route=[]


        if len(formatted_addresses) == 3:
            minprice_route.append("A) " + formatted_addresses[0])
            minprice_route.append("B) " + formatted_addresses[1])

        elif (len(formatted_addresses) == 5):
            if (result1cost > result2cost):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[2])
                minprice_route.append("C)" + formatted_addresses[3])
                minprice_route.append("D) " + formatted_addresses[1])

            elif (result2cost > result1cost):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[3])
                minprice_route.append("C) " + formatted_addresses[2])
                minprice_route.append("D) " + formatted_addresses[1])

        elif(len(formatted_addresses) == 6):
            if(Index_Min_Cost == 0):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[2])
                minprice_route.append("C) " + formatted_addresses[3])
                minprice_route.append("D) " + formatted_addresses[4])
                minprice_route.append("E) " + formatted_addresses[1])
            elif(Index_Min_Cost == 1):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[2])
                minprice_route.append("C) " + formatted_addresses[4])
                minprice_route.append("D) " + formatted_addresses[3])
                minprice_route.append("E) " + formatted_addresses[1])
            elif (Index_Min_Cost == 2):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[3])
                minprice_route.append("C) " + formatted_addresses[2])
                minprice_route.append("D) " + formatted_addresses[4])
                minprice_route.append("E) " + formatted_addresses[1])
            elif (Index_Min_Cost == 3):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[3])
                minprice_route.append("C) " + formatted_addresses[4])
                minprice_route.append("D) " + formatted_addresses[2])
                minprice_route.append("E) " + formatted_addresses[1])
            elif (Index_Min_Cost == 4):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[4])
                minprice_route.append("C) " + formatted_addresses[3])
                minprice_route.append("D) " + formatted_addresses[2])
                minprice_route.append("E) " + formatted_addresses[1])
            elif (Index_Min_Cost == 5):
                minprice_route.append("A) " + formatted_addresses[0])
                minprice_route.append("B) " + formatted_addresses[4])
                minprice_route.append("C) " + formatted_addresses[2])
                minprice_route.append("D) " + formatted_addresses[3])
                minprice_route.append("E) " + formatted_addresses[1])


      else: 
        lyft_metrics = []
        uber_metrics = []
        legs = []
        for calculator in [uber, lyft]:
          for leg in calculated_route['routes'][0]['legs']:
            start_lat = leg['start_location']['lat']
            start_lng = leg['start_location']['lng']
            end_lat = leg['end_location']['lat']
            end_lng = leg['end_location']['lng']
            legs.append((calculator, start_lat, start_lng, end_lat, end_lng))
        
        thread_pool = ThreadPool(8)
        price_list = thread_pool.map(get_route_metrics, legs)
        result_metrics = get_trip_stats_summary(price_list[0 : len(price_list)/2],
                                                price_list[len(price_list)/2 : len(price_list)])
        print("Min Distance Result: ", result_metrics)




      mindist_route =[]
      mindist_route.append("A) " + formatted_addresses[0])
      path_index = 'B'
      for waypoint_index in calculated_route['routes'][0]['waypoint_order']:
        mindist_route.append(path_index + ") " + formatted_addresses[2+waypoint_index])
        path_index = chr(ord(path_index) + 1)
      mindist_route.append(path_index + ") " + formatted_addresses[1])
      print "route : ",type(mindist_route)


      route= []
      if request.args['price_mode'] == "minprice" and waypoint_count > 1:
          route = minprice_route

      else:
          route = mindist_route



      return render_template('analysis.html', result=result_metrics, route=route)
  else:
      return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
