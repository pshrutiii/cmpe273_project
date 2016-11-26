import requests
import requests.auth


client_id = '8twZH-pOSBrFb4upXzhyOsFo4LPYrtP1'
secret ="hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS"

def Authorize():
    data = {
        'client_id': client_id,
        'response_type': 'code',
        'response_type':'code',
        'scope' : 'public',
        'state': 'avi',
        'redirect_uri':'https://youtube.com'
    }
    return requests.post('https://login.uber.com/oauth/v2/authorize',auth=requests.auth.HTTPBasicAuth(client_id,secret), json=data)

a = requests.get('https://api.uber.com/v1/estimates/price?start_latitude=37.625732&start_longitude=-122.377807&end_latitude=37.785114&end_longitude=-122.406677&server_token=hPnY1_4-AaaX7mDTrcV97UsQlmIHlDsgGf-ty0TS')

print(a.json())