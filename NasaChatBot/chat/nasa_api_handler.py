from .nasa_api import call_nasa_api

def handler(api_name, params):
    apod_title = apod_image = explanation = None
    neows_asteroids = None
    earth_image_url = None

    nasa_result = call_nasa_api(api_name, params)

    if api_name == "apod":
        apod_title = nasa_result.get('title')
        apod_image = nasa_result.get('image_url')
        explanation = nasa_result.get("description")
    elif api_name == "neows":
        asteroid_data = []
        neo_dict = nasa_result.get('data', {}).get("near_earth_objects", {})
        for date, asteroid in neo_dict.items():
            for obj in asteroid:
                approach = obj.get('close_approach_data', [{}])[0]
                est_diameter = obj.get("estimated_diameter", {}).get('meters', {})
                asteroid_data.append({
                    "name" : obj.get("name", "N/A"),
                    "date" : date, 
                    "distance_km" : round(float(approach.get("miss_distance", {}).get("kilometers", 0))),
                    "diameter_m" : round(est_diameter.get("estimated_diameter_max", 0), 1),
                    "velocity_kmph" : round(float(approach.get("relative_velocity", {}).get("kilometers_per_hour", 0))),
                })
        neows_asteroids = asteroid_data
        explanation = nasa_result.get("description", "")
    elif api_name == "earth":
        earth_image_url = nasa_result.get("image_url")
        explanation = nasa_result.get("description", "")

    return {
        "apod_title": apod_title,
        "apod_image": apod_image,
        "explanation": explanation,
        "neows_asteroids": neows_asteroids,
        "earth_image_url": earth_image_url,
    }