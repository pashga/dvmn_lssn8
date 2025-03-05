import json
import os
import folium
import requests

from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(distance_coffee):
    return distance_coffee["distance"]


def main():
    load_dotenv()
    new_json = []
    apikey = os.getenv("YA_API")
    place = input("Где вы находитесь? ")
    fetch_place = fetch_coordinates(apikey, place)
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_json = my_file.read()
        coffees = json.loads(file_json)
    for coffee in range(len(coffees)):
        title = coffees[coffee]["Name"]
        distance_coffee = distance.distance(
            fetch_place[::-1],
            (
                coffees[coffee]["geoData"]["coordinates"][1],
                coffees[coffee]["geoData"]["coordinates"][0]
            )
        ).km
        latitude = coffees[coffee]["Latitude_WGS84"]
        longitude = coffees[coffee]["Longitude_WGS84"]
        coffees_dict = {
            "title": title,
            "distance": distance_coffee,
            "latitude": latitude,
            "longitude": longitude,
        }
        new_json.append(coffees_dict)
    new_json = sorted(new_json, key=get_distance)
    new_json = new_json[:5]
    m = folium.Map(location=fetch_place[::-1])

    for coffee in range(len(new_json)):
        folium.Marker(
            location=[
                new_json[coffee]["latitude"],
                new_json[coffee]["longitude"]
            ],
            tooltip=new_json[coffee]["title"],
            popup=new_json[coffee]["title"],
            icon=folium.Icon(color="green"),
        ).add_to(m)
    m.save("index.html")

if __name__== "__main__":
    main()