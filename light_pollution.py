import requests
import math
import pandas as pd
from collections import OrderedDict

# Queries municipalities (wikidata Q2074737) within the radius from set point, ordered by distance
def query_function(lon, lat, radius, angle_max, angle_min):
    url = 'https://query.wikidata.org/sparql'
    query = '''
    SELECT DISTINCT ?Municipio ?Provincia ?poblacion ?distancia ?longitud ?latitud WHERE 
    {
        ?municipality wdt:P31 wd:Q2074737.
        ?municipality wdt:P1448 ?Municipio.
        ?province wdt:P31 wd:Q162620.
        ?municipality wdt:P131 ?province.
        ?province rdfs:label ?Provincia.
        SERVICE wikibase:around { 
            ?municipality wdt:P625 ?location . 
            bd:serviceParam wikibase:center "Point('''+str(lon)+''' '''+str(lat)+''')"^^geo:wktLiteral .
            bd:serviceParam wikibase:radius "'''+str(radius)+'''" . 
            bd:serviceParam wikibase:distance ?distancia .
        }
        ?municipality p:P625 ?coordinates .
        ?coordinates psv:P625 ?coordinate_node .
        ?coordinate_node wikibase:geoLatitude ?latitud .
        ?coordinate_node wikibase:geoLongitude ?longitud .
        ?municipality wdt:P1082 ?poblacion.
        FILTER(lang(?Provincia) = "es")
        FILTER(lang(?Municipio) = "es")
    }order by asc(?distancia)
    '''
    r = requests.get(url, params={'format': 'json', 'query': query})
    data = r.json()

    # Writes the json into pandas dataframe
    places = []
    for item in data['results']['bindings']:
        # check if the place is within the angle range
        if angle_range(lon, lat, float(item['longitud']['value']), float(item['latitud']['value']), angle_max, angle_min):
            places.append(OrderedDict({
                'Municipio': item['Municipio']['value'],
                'Provincia': item['Provincia']['value'],
                'Poblacion': item['poblacion']['value'],
                'Distancia': item['distancia']['value'],
                'lon': item['longitud']['value'],
                'lat': item['latitud']['value']}))
    df = pd.DataFrame(places)
    if not df.empty:
        df.set_index('Municipio', inplace=True)
        df = df.astype({'Poblacion': int, 'Distancia': float, 'lon': float, 'lat': float})
        df = df.round({'Distancia': 2, 'lon': 4, 'lat': 4})

    return df.reset_index()


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


if __name__ == '__main__':

    # Get latitude and convert into decimal format
    latitude = input("Please enter the latitude (xxº xx' xx'' N): ").split()
    latitude = float(latitude[0]) + (float(latitude[1])/60) + (float(latitude[2])/3600)

    # Get longitude and convert into decimal format
    longitude = input("Please enter the longitude: (xxº xx' xx'' W/E): ").split()
    sign = longitude[3]
    longitude = float(longitude[0]) + (float(longitude[1])/60) + (float(longitude[2])/3600)
    if sign == "W":
        longitude = longitude * -1

    # Get distance in kilometer
    distance = input('Please enter the radius (km): ')

    # Get the central angle
    angle = input('Please enter the central angle (º): ')

    # Get the angle opening
    opening = input('Please enter the angle opening (º): ')
    angle_max = (float(angle) + float(opening)/2) % 360
    angle_min = (float(angle) - float(opening)/2) % 360

    # pandas dataframe displays all columns
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)

    # pandas dataframe of municipalities in Spain that match conditions
    places = query_function(longitude, latitude, distance, angle_max, angle_min)

    if not places.empty:
        print(places[['Municipio', 'Provincia', 'Poblacion', 'Distancia']])
    else:
        print('No matching records found')