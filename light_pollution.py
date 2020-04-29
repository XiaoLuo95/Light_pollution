import requests
import time
import math
import pandas as pd
from collections import OrderedDict
import geopy.distance as dist

# global dataframe for full list of light pollution sources
df = pd.DataFrame()
# global dataframe storing the search parameters
iv = pd.DataFrame()

# Query full list of light pollution sources, including quarry, factory, greenhouse and shopping malls within Spain
def query_function():
    places = []

    wikidata_url = 'https://query.wikidata.org/sparql'
    wikidata_query = '''
    SELECT DISTINCT ?Municipio ?Provincia ?poblacion ?longitud ?latitud WHERE 
    {
        ?municipality wdt:P31 wd:Q2074737.
        ?municipality wdt:P1448 ?Municipio.
        ?province wdt:P31 wd:Q162620.
        ?municipality wdt:P131 ?province.
        ?province rdfs:label ?Provincia.
        ?municipality p:P625 ?coordinates .
        ?coordinates psv:P625 ?coordinate_node .
        ?coordinate_node wikibase:geoLatitude ?latitud .
        ?coordinate_node wikibase:geoLongitude ?longitud .
        ?municipality wdt:P1082 ?poblacion.
        FILTER(lang(?Provincia) = "es")
        FILTER(lang(?Municipio) = "es")
    }
    '''
    response_municipality = requests.get(wikidata_url, params={'format': 'json', 'query': wikidata_query})
    data_municipality = response_municipality.json()
    for item in data_municipality['results']['bindings']:
        # check if the place is within the angle range
            places.append(OrderedDict({
                'Nombre': item['Municipio']['value'],
                'Tipo': 'Municipio',
                'Provincia': item['Provincia']['value'],
                'Poblacion': round(float(item['poblacion']['value']), 0),
                'lon': item['longitud']['value'],
                'lat': item['latitud']['value']}))

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query_quarry = """
        [out:json];
        area["ISO3166-1"="ES"][admin_level=2];
        (
          node["landuse"="quarry"](area);
          way["landuse"="quarry"](area);
          relation["landuse"="quarry"](area);
        );
        out center;
        """
    response_quarry = requests.get(overpass_url, params={'data': overpass_query_quarry})
    data_quarry = response_quarry.json()

    for element in data_quarry['elements']:
        if 'name' in element['tags']:
            if element['type'] == 'node':
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Minas',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['lon'],
                    'lat': element['lat']}))
            elif 'center' in element:
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Minas',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['center']['lon'],
                    'lat': element['center']['lat']}))

    overpass_query_factory = """
        [out:json];
        area["ISO3166-1"="ES"][admin_level=2];
        (
          node["man_made"="works"](area);
          way["man_made"="works"](area);
          relation["man_made"="works"](area);
        );
        out center;
        """
    response_factory = requests.get(overpass_url, params={'data': overpass_query_factory})
    data_factory = response_factory.json()

    for element in data_factory['elements']:
        if 'name' in element['tags']:
            if element['type'] == 'node':
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Fábricas',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['lon'],
                    'lat': element['lat']}))
            elif 'center' in element:
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Fábricas',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['center']['lon'],
                    'lat': element['center']['lat']}))

    '''overpass_query_greenhouse = """
        [out:json];
        area["ISO3166-1"="ES"][admin_level=2];
        (
          node["landuse"="greenhouse_horticulture"](area);
          way["landuse"="greenhouse_horticulture"](area);
          relation["landuse"="greenhouse_horticulture"](area);
        );
        out center;
        """
    response_greenhouse = requests.get(overpass_url, params={'data': overpass_query_greenhouse})
    data_greenhouse = response_greenhouse.json()

    for element in data_greenhouse['elements']:
        if 'name' in element['tags']:
            if element['type'] == 'node':
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Invernadero',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['lon'],
                    'lat': element['lat']}))
            elif 'center' in element:
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Invernadero',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['center']['lon'],
                    'lat': element['center']['lat']}))
    '''

    overpass_query_shop = """
        [out:json];
        area["ISO3166-1"="ES"][admin_level=2];
        (
          node["shop"="mall"](area);
          way["shop"="mall"](area);
          relation["shop"="mall"](area);
        );
        out center;
        """
    response_shop = requests.get(overpass_url, params={'data': overpass_query_shop})
    data_shop = response_shop.json()

    for element in data_shop['elements']:
        if 'name' in element['tags']:
            if element['type'] == 'node':
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Centro Comercial',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['lon'],
                    'lat': element['lat']}))
            elif 'center' in element:
                places.append(OrderedDict({
                    'Nombre': element['tags']['name'],
                    'Tipo': 'Centro Comercial',
                    'Provincia': '',
                    'Poblacion': '',
                    'lon': element['center']['lon'],
                    'lat': element['center']['lat']}))

    global df
    df = pd.DataFrame(places)
    df.reset_index()
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})
    df.to_csv("light_pollution_sources.csv")

# Store input values received from console
def input_values():
    params = []
    # Get latitude and convert into decimal format
    latitude = input("Please enter the latitude (xxº xx' xx'' N): ").split()
    latitude = float(latitude[0]) + (float(latitude[1]) / 60) + (float(latitude[2]) / 3600)

    # Get longitude and convert into decimal format
    longitude = input("Please enter the longitude: (xxº xx' xx'' W/E): ").split()
    sign = longitude[3]
    longitude = float(longitude[0]) + (float(longitude[1]) / 60) + (float(longitude[2]) / 3600)
    if sign == "W":
        longitude = longitude * -1

    # Get distance in kilometer
    distance = input('Please enter the radius (km): ')

    # Get the central angle
    angle = input('Please enter the central angle (º): ')

    # Get the angle opening
    opening = input('Please enter the angle opening (º): ')
    angle_max = (float(angle) + float(opening) / 2) % 360
    angle_min = (float(angle) - float(opening) / 2) % 360

    params.append(OrderedDict({
        'lat': latitude,
        'lon': longitude,
        'distance': distance,
        'angle': angle,
        'angle_max': angle_max,
        'angle_min': angle_min
    }))

    global iv
    iv = pd.DataFrame(params)
    iv.reset_index()
    iv = iv.astype({'lat': float, 'lon': float, 'distance': float, 'angle': float, 'angle_max': float, 'angle_min': float})
    iv = iv.round({'lon': 4, 'lat': 4, 'distance': 2})

# Filter all conditions, including distance, angle, angle opening
def filter():
    global df
    global iv
    lat = float(iv['lat'])
    lon = float(iv['lon'])
    distance = float(iv['distance'])
    angle_max = float(iv['angle_max'])
    angle_min = float(iv['angle_min'])
    list = []
    for index, row in df.iterrows():
        # if the place is within the radius
        if float(dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km) <= distance:
            # if the place is within the angle range
            if angle_range(lon, lat, float(row['lon']), float(row['lat']), angle_max, angle_min):
                list.append(OrderedDict({
                    'Nombre': row['Nombre'],
                    'Tipo': row['Tipo'],
                    'Provincia': row['Provincia'],
                    'Poblacion': row['Poblacion'],
                    'Distancia': dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km
                }))

    result = pd.DataFrame(list)
    if not result.empty:
        result = result.astype({'Distancia': float})
        result = result.round({'Distancia': 2})
        result = result.sort_values(by='Distancia')
        result = result.reset_index()

    return result


# Checks if bearing lays within the range
def angle_range(lon1, lat1, lon2, lat2, angle_max, angle_min):
    # convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)


    d_lon = lon2 - lon1
    y = math.sin(d_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    brng = math.atan2(y, x)
    brng = math.degrees(brng)

    if angle_min > 180:
        angle_min = angle_min - 360

    # If the bearing falls out of the angle range, return False
    if brng < angle_min or brng > angle_max:
        return False

    return True


def auto():
    input_values()
    data = filter()

    if not data.empty:
        print(data[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia"]])
    else:
        print('No matching records found')

if __name__ == '__main__':
    '''
    print("Initializing...")
    print("The process will take about 75 seconds.")

    start = time.time()
    query_function()
    end = time.time()
    '''

    df = pd.read_csv("light_pollution_sources.csv")
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})
    pd.set_option('display.max_rows', None, 'display.max_columns', None)
    #print("Time spent: " + str(round((end - start), 2)) + "s")

    auto()
