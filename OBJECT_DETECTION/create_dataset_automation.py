import pymongo
import urllib3
import datetime
from geopy.geocoders import Nominatim
import random

GEOLOCATOR = Nominatim(user_agent="MyApp")
MONGO_CONNECTOR = pymongo.MongoClient("mongodb+srv://chsh7390:qwaszx1203@cluster0.0ap2wng.mongodb.net/?retryWrites=true&w=majority")
DATABASE = MONGO_CONNECTOR["KAVACH_NEW"]
COLLECTION = DATABASE["CRIME"]


CRIME_TYPES = ["Violence", "Street Crime", "Burglary"]
CRIME_LEVELS = ["High", "Low", "Moderate"]
CITIES = ["chennai", "bengaluru", "delhi", "mumbai",
          "jaipur", "pune", "kolkata", "hyderabad",
          "lucknow", "kanpur", "patna", "banaras", "ujjain"]
COORDINATES = []
CHOWKI = {}

def get_lat_lon_chowki() :
    global CITIES, COORDINATES, CHOWKI, GEOLOCATOR
    for _ in CITIES :
        location = GEOLOCATOR.geocode(_)
        COORDINATES.append([location.latitude,
                            location.longitude])
        CHOWKI[_] = []
        for __ in range(random.randint(1, 4)) :
            chowki_name = ""
            for ___ in range(random.randint(5, 10)) :
                chowki_name += "qazwsxedcrfvtgbyhnujmikolp"[random.randint(0, 25)]
            chowki_name = "CHOWKI " + chowki_name
            CHOWKI[_].append(chowki_name)

def update_random_data() :
    global CITIES, COORDINATES, CHOWKI, CRIME_TYPES, CRIME_LEVELS, COLLECTION
    #COLLECTION.drop()
    all_data = []
    for _ in range(200) :
        random_city_index = random.randint(0, len(CITIES) - 1)
        random_crime_index = random.randint(0, len(CRIME_TYPES) - 1)
        random_chawki_index = random.randint(0, len(CHOWKI[CITIES[random_city_index]]) - 1)
        data = {}
        data['city'] = CITIES[random_city_index].capitalize()
        data['coordinates'] = COORDINATES[random_city_index]
        data['level'] = CRIME_LEVELS[random_crime_index]
        data['reported'] = CHOWKI[CITIES[random_city_index]][random.randint(0, len(CHOWKI[CITIES[random_city_index]]) - 1)]
        data['nature'] = CRIME_TYPES[random_crime_index]
        data['time'] = datetime.datetime(2022,
                                         random.randint(1, 12), 
                                         random.randint(1, 28), 
                                         random.randint(0, 23),
                                         random.randint(0, 59),
                                         random.randint(0, 59))
        all_data.append(data)
    COLLECTION.insert_many(all_data)

if __name__ == "__main__" :
    get_lat_lon_chowki()
    update_random_data()
