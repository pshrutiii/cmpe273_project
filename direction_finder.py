# This file contains functions to interact with google.
import requests

# Waypoints is a string with waypoints joined by "|".
#
# Also leverage this api to solve travelling salesman problem.
def find_direction(key, origin, destination, waypoints):
  directions_rest_api = \
      "https://maps.googleapis.com/maps/api/directions/json?";

  directions_rest_api += "origin=" + origin
  directions_rest_api += "&destination=" + destination
  directions_rest_api += "&key=" + key

  # Solve travelling salesman problem for finding best route.
  directions_rest_api += "&waypoints="
  directions_rest_api  += "optimize:true|" + waypoints

  response = requests.get(directions_rest_api);

  if response.status_code != 200:
    return {}

  return response
