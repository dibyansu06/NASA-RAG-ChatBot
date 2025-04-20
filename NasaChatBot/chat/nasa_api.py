import requests
import os

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")


def call_apod_api(params):
    url = "https://api.nasa.gov/planetary/apod"
    params["api_key"] = NASA_API_KEY
    response = requests.get(url, params=params)
    print("apod_called", response)
    data = response.json()

    return {
        "api" : "apod",
        "title" : data.get("title", "Astronomy Picture of the Day"),
        "description" : data.get("explanation", ""),
        "image_url" : data.get("url", ""),
        'data' : data
    }

def call_neows_api(params):
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params["api_key"] = NASA_API_KEY
    response = requests.get(url, params=params)
    print("neows_called", response)
    data = response.json()
    
    count = data.get("element_count", 0)
    neos_by_date = data.get("near_earth_objects", {})

    summary = f"NASA detected {count} near-Earth objects during the selected time range."
    for date, objects in neos_by_date.items():
        summary += f"\n- {date} : {len(objects)} objects"

    return {
        "api" : "neows",
        "title" : "Near Earth Object Summary",
        "description" : summary,
        "image_url" : "",
        'data' : data
    }

def call_earth_api(params):
    url = "https://api.nasa.gov/planetary/earth/imagery"
    params["api_key"] = NASA_API_KEY
    response = requests.get(url, params=params)
    
    content_type = response.headers.get("Content-Type", "")
    if "image" in content_type:
        
        image_url = response.url  
        return {
            "api": "earth",
            "title": "Earth Imagery",
            "description": f"Satellite image for location ({params.get('lat')}, {params.get('lon')})",
            "image_url": image_url,
            "data": {}
        }

    try:
        data = response.json()
    except Exception as e:
        print("JSON decode failed:", e)
        return {
            "api": "earth",
            "title": "Error",
            "description": f"Failed to fetch Earth imagery. Non-image response: {response.text}",
            "image_url": "",
            "data": {}
        }

    return {
        "api": "earth",
        "title": "Error",
        "description": f"Earth imagery request did not return image. Response: {data}",
        "image_url": "",
        "data": data
    }



def call_nasa_api(api_name, params):
    if api_name == "apod":
        return call_apod_api(params)
    elif api_name == "neows":
        return call_neows_api(params)
    elif api_name == "earth":
        return call_earth_api(params)
    else:
       return {
            "api": api_name,
            "title": "Unsupported API",
            "description": f"The requested NASA API '{api_name}' is not currently supported.",
            "image_url": "",
            "data": {}
        }