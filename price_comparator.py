from cost_calculator import LyftCalculator, UberCalculator
from direction_finder import find_direction

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import render_template
from flask import request

app = Flask(__name__)

###################################
# Google API key.
MAPS_KEY = 'AIzaSyCs7YDHV5QF2QgJt8aJ1cKvFfxrIwSjsN0'
JS_API_KEY = 'AIzaSyBYXFWRwOAPQ03YrXRDfLheFkeV2nc0sAk'
###################################

@app.route("/trips")
def trips():
  origin = request.args['origin']
  destination = request.args['destination']
  waypoints = request.args['waypoints']
  formatted_addresses = request.args['formatted_addresses'].split("__||__")

  calculated_route = find_direction(MAPS_KEY, origin, destination, waypoints).json()

  lyft = LyftCalculator()
  uber = UberCalculator()

  lyft_metrics = []
  uber_metrics = []
  for leg in calculated_route['routes'][0]['legs']:
    start_lat = leg['start_location']['lat']
    start_lng = leg['start_location']['lng']
    end_lat = leg['end_location']['lat']
    end_lng = leg['end_location']['lng']
    lyft_metrics.append(lyft.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
    uber_metrics.append(uber.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
  
  combined_metrics = []
  for i in range(len(uber_metrics)):
    lyft_route_metrics = lyft_metrics[i]
    uber_route_metrics = uber_metrics[i]
    combined_route_metrics = lyft_route_metrics.copy()
    combined_route_metrics.update(uber_route_metrics)
    combined_metrics.append(combined_route_metrics)

  result_metrics = {}

  # NOTE: If we want to add additional options like UberXL, etc, just add a name here. 
  for company in ['uberX', 'Lyft', 'uberXL', 'Lyft Plus']: # ['uberXL', 'Lyft Plus', 'Lyft Line']
    values = {'name' : company.capitalize()}
    avg_cost = 0
    total_time = 0
    for i in range(len(combined_metrics)):
      avg_cost += combined_metrics[i][company]['low_price_dollars'] * combined_metrics[i][company]['multiplier']
      total_time += combined_metrics[i][company]['duration_sec'] / 60.0
    values['avg_cost'] = round(avg_cost / len(combined_metrics), 2)
    values['total_time'] = round(total_time, 1)
    result_metrics[company] = values
 
  route = []
  route.append("A) " + formatted_addresses[0])
  path_index = 'B'
  for waypoint_index in calculated_route['routes'][0]['waypoint_order']:
    route.append(path_index + ") " + formatted_addresses[2+waypoint_index])
    path_index = chr(ord(path_index) + 1)
  route.append(path_index + ") " + formatted_addresses[1])

  return render_template('analysis.html', result=result_metrics, route=route)

@app.route("/")
def price_comparator():
    global JS_API_KEY
    return render_template('price_comparator.html', maps_key=JS_API_KEY)

if __name__ == "__main__":
    app.run()
