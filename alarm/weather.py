import requests
import config
url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/351351"

response = requests.get(url, config.params).json()
w = ['It will be a clear night',
     'It will be a Sunny day',
     'It will be a Partly cloudy day', # night
     'It will be a Partly cloudy day', # day
     'Not used', # nice one
     'It will be a misty day',
     'It will be a foggy day',
     'It will be a cloudy day',
     'It will be a overcast day',
     'Today there will be Light rain showers', # night
     'Today there will be Light rain showers', # day
     'Today there will be Drizzle',
     'It will rain lightly today', # Light rain
     'Today there will be Heavy rain showers', # night
     'Today there will be Heavy rain showers', # day
     'It will rain heavily today', # Heavy rain
     'Today there will be Sleet showers', # night
     'Today there will be Sleet showers', # day
     'Today there will be Sleet',
     'Today there will be Hail showers', # night
     'Today there will be Hail showers', # day
     'Today there will be Hail',
     'Today there will be Light snow showers', # night
     'Today there will be Light snow showers', # day
     'Today there will be Light snow',
     'Today there will be Heavy snow showers', # night
     'Today there will be Heavy snow showers', # day
     'Today there will be Heavy snow',
     'Today there will be Thunder showers', # night
     'Today there will be Thunder showers', # day
     'Today will be Thundery']

v = {'UN': 'unknown',
     'VP': 'Very poor', # Less than 1 km
     'PO': 'Poor', # Between 1-4 km
     'MO': 'Moderate', # Between 4-10 km
     'GO': 'Good', # Between 10-20 km
     'VG': 'Very good', # Between 20-40 km
     'EX': 'Excellent' # More than 40 km
    }

today = response['SiteRep']['DV']['Location']['Period'][1]['Rep']

print(len(today))
now = None
for time_zone in today:
  if int(time_zone['$']) == 720:
    now = time_zone

if now is None:
  now = response['SiteRep']['DV']['Location']['Period'][1]['Rep'][0]

print(now['$'])
weather_type = w[int(now['W'])]
wind_speed = int(now['S'])
rain_prob = int(now['Pp'])
visibility = v[(now['V'])]
temperature = int(now['T'])
print(f"{weather_type} with temperatures of around {temperature} celcius, wind of around {wind_speed}mph, {visibility} visibility and {rain_prob}% chance of rain")

