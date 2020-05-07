import requests
import time
import numpy as np
import re
import argparse
import math
import pandas as pd
from collections import OrderedDict
import geopy.distance as dist

# command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("data", help = "file containing measurement data")
parser.add_argument("threshold", type=float, help = "percentage of magnitude from minimum under consideration [0.00-1.00]")
parser.add_argument("-o", "--opening", type=float, nargs=2, action="store", help="angle opening's lower and upper bound, separated by whitespace [0-360]")
parser.add_argument("-d", "--distance", type=float, action="store", help="radius in km within to search, default 200")
parser.add_argument("-n", "--cloudiness_angle", type=float, action="store", help="angle opening w.r.t. each original angle from data to be considered as same, in order to calculate the cloudiness to each place. Original angles spacing are 11º-12º, opening higher than 11º may cause overlap. [0-12]")
required = parser.add_argument_group('required arguments')
required.add_argument('-s', '--source', type=str, help = "data source type: sqm/tas", required=True)
args = parser.parse_args()

# global distance, default 200
distance = 200

# global m10 dataframe
m10 = pd.DataFrame(columns=['Mag', 'Azi', 'Cloudiness'])

# global dataframe for full list of light pollution sources
df = pd.DataFrame()

# global latitud and longitud
lat = None
lon = None

# global maximum and minimum angle in search
angle_min = None
angle_max = None

# global adjacent angles from original angles in tas
adj = None


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


# sqm file data reading
def read_file_sqm():
    # Encoding: Western Europe
    myFile = open(args.data, "r", encoding='iso8859_15')
    contents = myFile.read()
    myFile.close()

    # Load latitude and longitude
    global lat, lon
    lat = float(str(re.findall(r'# LATITUD: (.*)', contents)[0]).replace('\t', ""))
    lon = float(str(re.findall(r'# LONGITUD: (.*)', contents)[0]).replace('\t', ""))

    # Load and process the lowest cenit readings
    # Regex: get contents of m20
    m20 = str(re.findall(r'm20 = \[(.*)\]', contents)[0]).split(", ")
    for item in m20:
        item.replace(",", ".")
    m20 = np.array(m20, dtype=np.float32)

    # Get the difference between maximum and minimum values recorded as range
    # Regex: Get all contents between "[" and "]"
    magnitudes = re.findall(r'\[(.*)\]', contents)
    total = []
    for item in magnitudes:
        for x in item.split(", "):
            total.append(str(x).replace(",", "."))
    total = np.asfarray(total, float)
    total_range = (total.max() - total.min()).round(2)

    # Threshold, set as 30% of the range from minimum
    th = m20.min() + float(args.threshold) * total_range

    global angle_max, angle_min
    # If optional opening is set with values, just set the global, otherwise proceed to calculate them
    if args.opening is not None:
        angle_min = args.opening[0]
        angle_max = args.opening[1]
    else:
        # Angles at left and right position of the minimum value
        angle_left = m20[int(np.where(m20 == m20.min())[0] - 1) % 12]
        angle_right = m20[int(np.where(m20 == m20.min())[0] + 1) % 12]

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 60º, otherwise 30º
        if angle_left < angle_right:
            angle_min = angle_left
            angle_max = m20.min()
        elif angle_right < angle_left:
            angle_min = m20.min()
            angle_max = angle_right
        else:
            angle_min = angle_left
            angle_max = angle_right

        # If value at right of min is within threshold and less than the angle_right, update
        # break loop if value surpass threshold
        idx = int(np.where(m20 == m20.min())[0])
        for aux in range(int(idx + 1), int(idx + 12)):
            if m20[aux % 12] <= th:
                if m20[aux % 12] < angle_right:
                    angle_right = m20[aux % 12]
            else:
                break

        # If value at left of min is within threshold and less than the angle_left, update
        # break loop if value surpass threshold
        for aux in range(idx - 1, idx - 12, -1):
            if m20[aux % 12] <= th:
                if m20[aux % 12] > angle_left:
                    angle_left = m20[aux % 12]
            else:
                break

        # Convert angle_left and angle_right to real angles:
        angle_min = int(np.where(m20 == angle_left)[0]) * 30
        angle_max = int(np.where(m20 == angle_right)[0]) * 30


# tas file data reading
def read_file_tas():
    myFile = open(args.data, "r", encoding='iso8859_15')

    # twice readline to skip first heading line
    lines = myFile.readlines()[1:]
    myFile.close()
    latlon = lines[0].split()

    # get latitude and longitude from first data line
    global lat, lon
    lat_a = latlon[9].split(":")
    lon_a = latlon[10].split(":")
    lat = float(lat_a[0]) + float(lat_a[1])/60 + float(lat_a[2])/3600
    lon = float(lon_a[0]) + float(lon_a[1])/60 + float(lat_a[2])/3600

    # get useful information: T_IR, T_Sens, Mag, Azi of m10, and max & min value in Mag
    global m10
    mag_max = float(latlon[5])
    mag_min = float(latlon[5])
    for line in lines:
        sp = line.split()
        if sp[7] == '10.0':
            cloudiness = 100 - 3 * (float(sp[4]) - float(sp[3]))
            m10 = m10.append({'Mag': sp[5], 'Azi': sp[8], 'Cloudiness': cloudiness}, ignore_index=True)
        if float(sp[5]) > mag_max:
            mag_max = float(sp[5])
        elif float(sp[5]) < mag_min:
            mag_min = float(sp[5])
    m10 = m10.astype({'Mag': float, 'Azi': float, 'Cloudiness': float})
    m10 = m10.round({'Mag': 2, 'Azi': 2, 'Cloudiness': 2})
    mag_range = mag_max - mag_min

    # Threshold, set as 30% of the range from minimum
    th = mag_min + float(args.threshold) * mag_range

    global angle_max, angle_min
    # If optional opening is set with values, just set the global, otherwise proceed to calculate them
    if args.opening is not None:
        angle_min = args.opening[0]
        angle_max = args.opening[1]
    else:
        # Angles at left and right position of the minimum value
        angle_left = m10.loc[[(m10['Mag'].argmin() - 1) % len(m10)]]['Mag'].item()
        angle_right = m10.loc[[(m10['Mag'].argmin() + 1) % len(m10)]]['Mag'].item()

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 60º, otherwise 30º
        if angle_left < angle_right:
            angle_min = angle_left
            angle_max = m10['Mag'].min()
        elif angle_right < angle_left:
            angle_min = m10['Mag'].min()
            angle_max = angle_right
        else:
            angle_min = angle_left
            angle_max = angle_right

        # If value at right of min is within threshold and less than the angle_right, update
        # break loop if value surpass threshold
        idx = m10['Mag'].argmin()
        for aux in range(idx + 1, idx + len(m10)):
            if m10.loc[[aux % len(m10)]]['Mag'].item() <= th:
                if m10.loc[[aux % len(m10)]]['Mag'].item() < angle_right:
                    angle_right = m10.loc[[aux % len(m10)]]['Mag'].item()
            else:
                break

        # If value at left of min is within threshold and less than the angle_left, update
        # break loop if value surpass threshold
        for aux in range(idx - 1, idx - len(m10), -1):
            if m10.loc[[aux % len(m10)]]['Mag'].item() <= th:
                if m10.loc[[aux % len(m10)]]['Mag'].item() > angle_left:
                    angle_left = m10.loc[[aux % len(m10)]]['Mag'].item
            else:
                break

        # Store angle opening's lower and upper bounds
        angle_min = m10.loc[m10['Mag'] == angle_left]['Azi'].item()
        angle_max = m10.loc[m10['Mag'] == angle_right]['Azi'].item()


# Filter all conditions, including distance and angle opening
def filter():
    global df
    global m10
    global latitude, longitude, distance, angle_max, angle_min
    global adj

    # convert upper bound (0-360) into (-180, 180)
    if angle_max > 180:
        max_a = angle_max - 360
    else:
        max_a = angle_max

    # convert lower bound (0-360) into (-180, 180)
    if angle_min > 180:
        min_a = angle_min - 360
    else:
        min_a = angle_min

    # get sublist of original angles from tas within the global angle opening for tas with -n
    if adj is not None:
        if (angle_max + adj) % 360 > (angle_min - adj) % 360:
            m10 = m10[(m10['Azi'] >= angle_min - adj) & (m10['Azi'] <= angle_max + adj)].reset_index(drop=True)
        else:
            m10 = m10[(m10['Azi'] >= angle_max - adj) | (m10['Azi'] <= angle_min + adj)].reset_index(drop=True)
    list = []
    for index, row in df.iterrows():
        # if the place is within the radius
        if float(dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km) <= distance:
            # if the place is within the angle range
            angle = bearing(lon, lat, float(row['lon']), float(row['lat']))
            cloudiness = "-"
            if max_a < min_a:
                if angle >= min_a or angle <= max_a:
                    if angle < 0:
                        angle = angle + 360
                    for idx, r in m10.iterrows():
                        inf = float(r['Azi'].item() - adj) % 360
                        sup = float(r['Azi'].item() + adj) % 360
                        # transition from 360º to 0º
                        if inf < sup:
                            if check(angle, inf, sup):
                                cloudiness = r['Cloudiness'].item()
                        else:
                            if angle >= inf or angle <= sup:
                                cloudiness = r['Cloudiness'].item()
                    list.append(OrderedDict({
                        'Nombre': row['Nombre'],
                        'Tipo': row['Tipo'],
                        'Provincia': row['Provincia'],
                        'Poblacion': row['Poblacion'],
                        'Distancia': dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km,
                        'Dirección': angle,
                        'Nubosidad': cloudiness
                    }))
            else:
                if min_a <= angle <= max_a:
                    if angle < 0:
                        angle = angle + 360
                    for idx, r in m10.iterrows():
                        inf = float(r['Azi'].item() - adj) % 360
                        sup = float(r['Azi'].item() + adj) % 360
                        # transition from 360º to 0º
                        if inf < sup:
                            if check(angle, inf, sup):
                                cloudiness = r['Cloudiness'].item()
                        else:
                            if angle >= inf or angle <= sup:
                                cloudiness = r['Cloudiness'].item()
                    list.append(OrderedDict({
                        'Nombre': row['Nombre'],
                        'Tipo': row['Tipo'],
                        'Provincia': row['Provincia'],
                        'Poblacion': row['Poblacion'],
                        'Distancia': dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km,
                        'Dirección': angle,
                        'Nubosidad': cloudiness
                    }))

    result = pd.DataFrame(list)
    if not result.empty:
        result = result.astype({'Distancia': float, 'Dirección': float})
        result = result.round({'Distancia': 2, 'Dirección': 2})
        result = result.sort_values(by='Distancia')
        result = result.reset_index()

    return result


# Get the bearing from coordinate 1 to coordinate 2
# Angle range (-180, 180)
def bearing(lon1, lat1, lon2, lat2):
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

    return brng


# Check if a float number is within certain range
def check(original, inf, sup):
    if inf <= original <= sup:
        return True
    return False


# Automatic execution for sqm data
def auto_sqm():
    read_file_sqm()
    data = filter()

    if not data.empty:
        data = data[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección"]]
        data.to_csv('result.csv')
        print('Result saved in: result.csv')
    else:
        print('No matching records found')


# Automatic execution for tas data
def auto_tas():
    read_file_tas()
    data = filter()

    if not data.empty:
        data = data[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección", "Nubosidad"]]
        data.to_csv("result.csv")
        print("Result saved in: result.csv")
    else:
        print("No matching records found")


if __name__ == '__main__':
    '''
    print("Initializing...")
    print("The process will take about 75 seconds.")

    start = time.time()
    query_function()
    end = time.time()
    '''
    if args.cloudiness_angle is not None:
        if args.source.lower() != 'tas':
            parser.error('Sorry, the cloudiness angle opening is only supported for tas')
        elif not check(float(args.cloudiness_angle), 0, 12):
            parser.error('Please, the angle opening must be less or equal than 11 due to the spacing of original angles, otherwise would cause overlap')
        else:
            adj = float(args.cloudiness_angle) / 2

    if args.distance is not None:
        distance = args.distance

    df = pd.read_csv("light_pollution_sources.csv")
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})
    pd.set_option('display.max_rows', None, 'display.max_columns', None)
    '''print("Time spent: " + str(round((end - start), 2)) + "s")'''

    if args.source.lower() == 'sqm':
        auto_sqm()
    elif args.source.lower() == 'tas':
        auto_tas()
    else:
        parser.error('Please specify the input data type: sqm/tas')