# NOTE: This file leverages/references code present in liftupdate.py.

# This module is responsible for calculating costs
# for a given path(longitude, latitude). We would 
# implement various classes for the same.
import requests

# API using REST-API provided by UBER.
class UberCalculator(object):
  def __init__(self):
    self.uber_rest_api = \
      "https://api.uber.com/v1/estimates/price?server_token=hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS" 

  def get_route_metrics(self, start_latitude, start_longitude,
                 end_latitude, end_longitude):
    query = self.uber_rest_api

    # Construct GET query parameters.
    query += "&start_latitude=" + str(start_latitude)
    query += "&start_longitude=" + str(start_longitude)
    query += "&end_latitude=" + str(end_latitude)
    query += "&end_longitude=" + str(end_longitude)
    
    response = requests.get(query)

    # If response is not ok, return an empty map. 
    if response.status_code != 200: 
      return {}

    price_map = {}
    for packet in response.json()['prices']:
      # TODO: handle the case when no costs are returned, return appropriate errors.
      price_map[packet['display_name']] = \
          {'low_price_dollars' : packet['low_estimate'],
           'high_price_dollars' : packet['high_estimate'],
           'multiplier' : packet['surge_multiplier'],
           'duration_sec' : packet['duration']}
    return price_map

class LyftCalculator(object):
  def __init__(self):
    self.client_id_ = 'njKAAMEoDFge'
    self.client_secret_ = 'oQf6gnjZLNKfugCqgVJIwF06rgbHpwpA'
    self.lyft_res_api = \
        "https://api.lyft.com/v1/cost?"

  def get_authorization_token(self):
    response = requests.post("https://api.lyft.com/oauth/token",
        auth=requests.auth.HTTPBasicAuth(self.client_id_, self.client_secret_),
        json={'grant_type' : 'client_credentials', 'scope' : 'public'})
    return response.json()['access_token']

  def get_route_metrics(self, start_latitude, start_longitude,
                 end_latitude, end_longitude):
    auth_token = self.get_authorization_token()
    
    query = self.lyft_res_api

    # Construct GET query parameters.
    query += "&start_lat=" + str(start_latitude)
    query += "&start_lng=" + str(start_longitude)
    query += "&end_lat=" + str(end_latitude)
    query += "&end_lng=" + str(end_longitude)
    
    response = requests.get(query, headers={'Authorization' : 'Bearer ' + str(auth_token) })
    
    price_map = {}
    for packet in response.json()['cost_estimates']:
      # TODO: handle the case when no costs are returned, return appropriate errors.
      price_map[packet['display_name']] = \
          {'low_price_dollars' : packet['estimated_cost_cents_min'] / 100,
           'high_price_dollars' : packet['estimated_cost_cents_max'] / 100,
           'multiplier' : 1 + float(packet['primetime_percentage'][:-1]) / 100.0,
           'duration_sec' : packet['estimated_duration_seconds']}
    return price_map
