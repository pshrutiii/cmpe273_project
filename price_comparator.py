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

  ans = find_direction(MAPS_KEY, origin, destination, waypoints).json()

  lyft = LyftCalculator()
  uber = UberCalculator()

  lyft_metrics = []
  uber_metrics = []
  for leg in ans['routes'][0]['legs']:
    start_lat = leg['start_location']['lat']
    start_lng = leg['start_location']['lng']
    end_lat = leg['end_location']['lat']
    end_lng = leg['end_location']['lng']
    lyft_metrics.append(lyft.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
    uber_metrics.append(uber.get_route_metrics(start_lat, start_lng, end_lat, end_lng))
  
  result = {'lyft' : lyft_metrics, 'uber' : uber_metrics, 
            'waypoint_order' : ans['routes'][0]['waypoint_order']}
  print result
  return render_template('analysis.html', lyft=lyft_metrics, uber=uber_metrics)

@app.route("/")
def price_comparator():
    global JS_API_KEY
    return render_template('price_comparator.html', maps_key=JS_API_KEY)

if __name__ == "__main__":
    app.run()
