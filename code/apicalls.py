import requests

# Put your CENT Ischool IoT Portal API KEY here.
APIKEY = "4ea531e51c4d8b6360b3656a"

def get_google_place_details(google_place_id: str) -> dict:
    base_url = "https://cent.ischool-iot.net/api/google/places/details"
    headers = {"X-API-KEY": APIKEY}
    params = {"place_id": google_place_id}
    resp = requests.get(base_url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()
    
def get_azure_sentiment(text: str) -> dict:
    url = "https://cent.ischool-iot.net/api/azure/sentiment"
    headers = {"X-API-KEY": APIKEY}
    data = {"text": text}
    result = requests.post(url, headers=headers, data=data)
    result.raise_for_status()
    return result.json()

def get_azure_key_phrase_extraction(text: str) -> dict:
    url = "https://cent.ischool-iot.net/api/azure/keyphrasextraction"
    headers = {"X-API-KEY": APIKEY}
    body = {"text": text}
    r = requests.post(url, headers=headers, data=body)
    r.raise_for_status()
    return r.json()

def get_azure_named_entity_recognition(text: str) -> dict:
    url = "https://cent.ischool-iot.net/api/azure/entityrecognition"
    headers = {"X-API-KEY": APIKEY}
    payload = {"text": text}
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def geocode(place:str) -> dict:
    '''
    Given a place name, return the latitude and longitude of the place.
    Written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'location': place }
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def get_weather(lat: float, lon: float) -> dict:
    '''
    Given a latitude and longitude, return the current weather at that location.
    written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'lat': lat, 'lon': lon, 'units': 'imperial' }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary