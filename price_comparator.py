import MySQLdb
import gc

from connectdb import *
from cost_calculator import LyftCalculator, UberCalculator
from direction_finder import find_direction
from flask import render_template,redirect,request,url_for,g, session,flash
from flask import Flask
from passlib.hash import sha256_crypt
from wtforms import Form,TextField,PasswordField,validators

app = Flask(__name__)

db = MySQLdb.connect(host="localhost",  # host
                     user="root",  # username
                     passwd="root",  # password
                     db="CMPE273")  # db name
cur = db.cursor()

###################################
DB_USER_TABLE = "user_table"

# Google API key.
MAPS_KEY = 'AIzaSyCs7YDHV5QF2QgJt8aJ1cKvFfxrIwSjsN0'
JS_API_KEY = 'AIzaSyBYXFWRwOAPQ03YrXRDfLheFkeV2nc0sAk'
###################################

global jsdata
jsdata =""

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    global jsdata
    jsdata = request.form['javascript_data']
    return jsdata

@app.route('/addtag')
def add_tag():
      a = request.args.get('a', 0, type=str)
      l = request.args.get('l', 0, type=str)
      print "Added " + a + " -->> " + l
      Mysql2 = Mysql()
      Mysql2.insert('tags', User_id=1, TAGaddress=a, TAGname=l)
      return "nothing"

@app.route("/", methods =['GET', 'POST'])
def price_comparator():
    if g.user:
        try:
            global JS_API_KEY
            username = session['user']
            query_results = \
                    cur.execute("SELECT * from user_table WHERE Login_id = '%s' " % (username))
            user_table_row = list(cur.fetchall())[0]

            tag_selection_query = \
                    "SELECT * from tags WHERE user_id = '%s'" % str(user_table_row[0])
            print tag_selection_query
            #cur.execute(tag_selection_query)
            #allRows = {}
            #for row in cur.fetchall():
            #    print row[3] + " ---->>> " + row[2]
            #    allRows[row[3]] = row[2]  # adding to dictionary
            #dictVal = json.dumps(allRows)
            #print "Dict val is " + str(dictVal)
            dictVal = {}
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
    print "logout"


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
                 return redirect(url_for('price_comparator'))

        return render_template("register.html", form=form )

    except Exception as e:
        return (str(e))

##############################################################################
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
    # origin -> waypoint1 -> waypoint2 -> destination
    if (len(all_way_points_in_list) == 2):
        result1 = {}
        lyft_list1 = []
        uber_list1 = []

        a1 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        lyft_list1.append(a1)
        b1 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        lyft_list1.append(b1)
        c1= lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        lyft_list1.append(c1)

        p1 = uber.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        uber_list1.append(p1)
        q1 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        uber_list1.append(q1)
        r1 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        uber_list1.append(r1)

        combined_list1 = []

        for i in range(len(uber_list1)):
          lyft_route_metrics = lyft_list1[i]
          uber_route_metrics = uber_list1[i]
          combined_route_metrics = lyft_route_metrics.copy()
          combined_route_metrics.update(uber_route_metrics)
          combined_list1.append(combined_route_metrics)

        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost1 = 0
            total_time1 = 0

            for i in range(len(combined_list1)):
                cost1 += combined_list1[i][company]['low_price_dollars'] * combined_list1[i][company]['multiplier']
                values['cost'] = round(cost1, 2)
                total_time1 += combined_list1[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time1, 1)
                result1[company] = values
        print("Result1 : ", result1)

        #origin -> waypoint2 -> waypoint1 -> destination
        result2 = {}
        lyft_list2 = []
        uber_list2 = []
        a2 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        lyft_list2.append(a2)
        b2 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        lyft_list2.append(b2)
        c2= lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        lyft_list2.append(c2)

        p2 = uber.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        uber_list2.append(p2)
        q2 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        uber_list2.append(q2)
        r2 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        uber_list2.append(r2)

        combined_list2 = []

        for i in range(len(uber_list2)):
          lyft_route_metrics = lyft_list2[i]
          uber_route_metrics = uber_list2[i]
          combined_route_metrics = lyft_route_metrics.copy()
          combined_route_metrics.update(uber_route_metrics)
          combined_list2.append(combined_route_metrics)

        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost2 = 0
            total_time2 = 0

            for i in range(len(combined_list2)):
                cost2 += combined_list2[i][company]['low_price_dollars'] * combined_list2[i][company]['multiplier']
                total_time2 += combined_list2[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time2, 1)
                values['cost'] = round(cost2, 2)
                result2[company] = values
        print("Result2 : ", result2)

        # 3 way points
        # origin -> waypoint1 -> waypoint2 -> waypoint3 -> destination
    if (len(all_way_points_in_list) == 3):
        result1 = {}
        lyft_list1 = []
        uber_list1 = []

        a1 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        lyft_list1.append(a1)
        b1 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        lyft_list1.append(b1)
        c1= lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng)
        lyft_list1.append(c1)
        d1= lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)
        lyft_list1.append(d1)

        p1 = uber.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        uber_list1.append(p1)
        q1 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        uber_list1.append(q1)
        r1 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng)
        uber_list1.append(r1)
        s1 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)
        uber_list1.append(s1)

        combined_list1 = []

        for i in range(len(uber_list1)):
            lyft_route_metrics = lyft_list1[i]
            uber_route_metrics = uber_list1[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list1.append(combined_route_metrics)


        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost1 = 0
            total_time1 = 0

            for i in range(len(combined_list1)):
                cost1 += combined_list1[i][company]['low_price_dollars'] * combined_list1[i][company]['multiplier']
                total_time1 += combined_list1[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time1, 1)
                values['cost'] = round(cost1, 2)
                result1[company] = values
        print("Result1 : ", result1)

        # origin -> waypoint1 -> waypoint3 -> waypoint2 -> destination
        result2 = {}
        lyft_list2 = []
        uber_list2 = []

        a2 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        lyft_list2.append(a2)
        b2 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng)
        lyft_list2.append(b2)
        c2 = lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng)
        lyft_list2.append(c2)
        d2 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        lyft_list2.append(d2)

        p2 = uber.get_route_metrics(origin_lat, origin_lng, waypoint1_lat, waypoint1_lng)
        uber_list2.append(p2)
        q2 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng)
        uber_list2.append(q2)
        r2 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng)
        uber_list2.append(r2)
        s2 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        uber_list2.append(s2)

        combined_list2 = []

        for i in range(len(uber_list2)):
            lyft_route_metrics = lyft_list2[i]
            uber_route_metrics = uber_list2[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list2.append(combined_route_metrics)


        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost2 = 0
            total_time2 = 0

            for i in range(len(combined_list2)):
                cost2 += combined_list2[i][company]['low_price_dollars'] * combined_list2[i][company]['multiplier']
                total_time2 += combined_list2[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time2, 1)
                values['cost'] = round(cost2, 2)
                result2[company] = values
        print("Result2 : ", result2)


        # origin -> waypoint2 -> waypoint1 -> waypoint3 -> destination
        result3 = {}
        lyft_list3 = []
        uber_list3 = []

        a3 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        lyft_list3.append(a3)
        b3 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        lyft_list3.append(b3)
        c3 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng)
        lyft_list3.append(c3)
        d3 = lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)
        lyft_list3.append(d3)

        p3 = uber.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        uber_list3.append(p3)
        q3 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        uber_list3.append(q3)
        r3 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint3_lat, waypoint3_lng)
        uber_list3.append(r3)
        s3 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, destination_lat, destination_lng)
        uber_list3.append(s3)

        combined_list3 = []

        for i in range(len(uber_list3)):
            lyft_route_metrics = lyft_list3[i]
            uber_route_metrics = uber_list3[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list3.append(combined_route_metrics)

        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost3 = 0
            total_time3 = 0
            for i in range(len(combined_list3)):
                cost3 += combined_list3[i][company]['low_price_dollars'] * combined_list3[i][company]['multiplier']
                total_time3 += combined_list3[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time3, 1)
                values['cost'] = round(cost3, 2)
                result3[company] = values
        print("Result3 : ", result3)

        # origin -> waypoint2 -> waypoint3 -> waypoint1 -> destination
        result4 = {}
        lyft_list4 = []
        uber_list4 = []
        a4 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        lyft_list4.append(a4)
        b4 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng)
        lyft_list4.append(b4)
        c4 = lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng)
        lyft_list4.append(c4)
        d4 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        lyft_list4.append(d4)

        p4 = uber.get_route_metrics(origin_lat, origin_lng, waypoint2_lat, waypoint2_lng)
        uber_list4.append(p4)
        q4 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint3_lat, waypoint3_lng)
        uber_list4.append(q4)
        r4 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng)
        uber_list4.append(r4)
        s4 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        uber_list4.append(s4)

        combined_list4 = []

        for i in range(len(uber_list4)):
            lyft_route_metrics = lyft_list4[i]
            uber_route_metrics = uber_list4[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list4.append(combined_route_metrics)

        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost4 = 0
            total_time4 = 0
            for i in range(len(combined_list4)):
                cost4 += combined_list4[i][company]['low_price_dollars'] * combined_list4[i][company]['multiplier']
                total_time4 += combined_list4[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time4, 1)
                values['cost'] = round(cost4, 2)
                result4[company] = values
        print("Result4 : ", result4)

        # origin -> waypoint3 -> waypoint2 -> waypoint1 -> destination
        result5 = {}
        lyft_list5 = []
        uber_list5 = []
        a5 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint3_lat, waypoint3_lng)
        lyft_list5.append(a5)
        b5 = lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng)
        lyft_list5.append(b5)
        c5 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        lyft_list5.append(c5)
        d5 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        lyft_list5.append(d5)

        p5 = uber.get_route_metrics(origin_lat, origin_lng, waypoint3_lat, waypoint3_lng)
        uber_list5.append(p5)
        q5 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint2_lat, waypoint2_lng)
        uber_list5.append(q5)
        r5 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, waypoint1_lat, waypoint1_lng)
        uber_list5.append(r5)
        s5 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, destination_lat, destination_lng)
        uber_list5.append(s5)

        combined_list5 = []

        for i in range(len(uber_list5)):
            lyft_route_metrics = lyft_list5[i]
            uber_route_metrics = uber_list5[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list5.append(combined_route_metrics)

        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost5 = 0
            total_time5 = 0
            for i in range(len(combined_list5)):
                cost5 += combined_list5[i][company]['low_price_dollars'] * combined_list5[i][company]['multiplier']
                total_time5 += combined_list5[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time5, 1)
                values['cost'] = round(cost5, 2)
                result5[company] = values
        print("Result5 : ", result5)

        # origin -> waypoint3 -> waypoint1 -> waypoint2 -> destination
        result6 = {}
        lyft_list6 = []
        uber_list6 = []
        a6 = lyft.get_route_metrics(origin_lat, origin_lng, waypoint3_lat, waypoint3_lng)
        lyft_list6.append(a6)
        b6 = lyft.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng)
        lyft_list6.append(b6)
        c6 = lyft.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        lyft_list6.append(c6)
        d6 = lyft.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        lyft_list6.append(d6)

        p6 = uber.get_route_metrics(origin_lat, origin_lng, waypoint3_lat, waypoint3_lng)
        uber_list6.append(p6)
        q6 = uber.get_route_metrics(waypoint3_lat, waypoint3_lng, waypoint1_lat, waypoint1_lng)
        uber_list6.append(q6)
        r6 = uber.get_route_metrics(waypoint1_lat, waypoint1_lng, waypoint2_lat, waypoint2_lng)
        uber_list6.append(r6)
        s6 = uber.get_route_metrics(waypoint2_lat, waypoint2_lng, destination_lat, destination_lng)
        uber_list6.append(s6)

        combined_list6 = []

        for i in range(len(uber_list6)):
            lyft_route_metrics = lyft_list6[i]
            uber_route_metrics = uber_list6[i]
            combined_route_metrics = lyft_route_metrics.copy()
            combined_route_metrics.update(uber_route_metrics)
            combined_list6.append(combined_route_metrics)


        for company in ['Lyft', 'Lyft Plus','uberX','uberXL']:  # ['uberXL', 'Lyft Plus', 'Lyft Line']
            values = {'name': company.capitalize()}
            cost6 = 0
            total_time6 = 0
            for i in range(len(combined_list6)):
                cost6 += combined_list6[i][company]['low_price_dollars'] * combined_list6[i][company]['multiplier']
                total_time6 += combined_list6[i][company]['duration_sec'] / 60.0
                values['total_time'] = round(total_time6, 1)
                values['cost'] = round(cost6, 2)
                result6[company] = values
        print("Result6 : ", result6)


    if(len(all_way_points_in_list) == 2):
        result1cost = result1['Lyft Plus']['cost']
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

        final_result_metrics = eval("result" + str(1 + results.index(min(results))))
    return final_result_metrics

@app.route("/trips")
def trips():
  if g.user:
      print "Mode selected is " + str(jsdata)
      origin = request.args['origin']
      origin_lat_long_list= origin.split(',')
      origin_lat =  origin_lat_long_list[0]
      origin_lng =  origin_lat_long_list[1]

      destination = request.args['destination']
      destination_lat_long_list= destination.split(',')
      destination_lat = destination_lat_long_list[0]
      destination_lng = destination_lat_long_list[1]

      waypoints = request.args['waypoints']

      formatted_addresses = request.args['formatted_addresses'].split("__||__")
      print formatted_addresses

      lyft = LyftCalculator()
      uber = UberCalculator()
      #####################################################################################
      calculated_route = find_direction(MAPS_KEY, origin, destination, waypoints).json()

      lyft_metrics = []
      uber_metrics = []
      for leg in calculated_route['routes'][0]['legs']:
        start_lat = leg['start_location']['lat']
        start_lng = leg['start_location']['lng']
        end_lat = leg['end_location']['lat']
        end_lng = leg['end_location']['lng']
        lyft_metrics.append(lyft.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
        uber_metrics.append(uber.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
      # print "LYFT : ",lyft_metrics # avdeep   we have to take out price from here
      # print "UBER : ",uber_metrics #avdeep
      combined_metrics = []
      for i in range(len(uber_metrics)):
        lyft_route_metrics = lyft_metrics[i]
        uber_route_metrics = uber_metrics[i]
        combined_route_metrics = lyft_route_metrics.copy()
        combined_route_metrics.update(uber_route_metrics)
        combined_metrics.append(combined_route_metrics)
      #print "COMBINED :", combined_metrics # avdeep same as the above one to take out price from it
      result_metrics = {}

      # NOTE: If we want to add additional options like UberXL, etc, just add a name here.
      for company in ['uberX', 'Lyft', 'uberXL', 'Lyft Plus']: # ['uberXL', 'Lyft Plus', 'Lyft Line']
        values = {'name' : company.capitalize()}
        min_cost = 0
        total_time = 0
        for i in range(len(combined_metrics)):
          min_cost += combined_metrics[i][company]['low_price_dollars'] * combined_metrics[i][company]['multiplier']
          total_time += combined_metrics[i][company]['duration_sec'] / 60.0
        values['cost'] = round(min_cost, 2)
        values['total_time'] = round(total_time, 1)
        result_metrics[company] = values
      # print("Result : ",result_metrics) #avdeep final things to print like cost

      if(jsdata == "minprice"):
        waypoint_count = len(waypoints.split("|"))
        if waypoint_count > 1:
            result_metrics = \
                calculate_min_price_metrics(lyft, uber, waypoints, origin_lat,
                        origin_lng, destination_lat, destination_lng)

      route = []
      route.append("A) " + formatted_addresses[0])
      path_index = 'B'
      for waypoint_index in calculated_route['routes'][0]['waypoint_order']:
        route.append(path_index + ") " + formatted_addresses[2+waypoint_index])
        path_index = chr(ord(path_index) + 1)
      route.append(path_index + ") " + formatted_addresses[1])

      return render_template('analysis.html', result=result_metrics, route=route)
  else:
      return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
