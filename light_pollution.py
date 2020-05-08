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
parser.add_argument("-t", "--threshold_percent", type=float, action="store",
                    help="percentage of magnitude from minimum to consider. Default 0.3. Incompatible with {-T, -o}. [0.00-1.00]")
parser.add_argument("-T", "--threshold_mag", type=float, action="store",
                    help="maximum magnitude under consideration. Incompatible with {-t, -o}.")
parser.add_argument("-o", "--opening", type=float, nargs=2, action="store",
                    help="angle opening's lower and upper bound, separated by whitespace. Incompatible with {-t, -T}. [0-359.99] [0-359.99]")
parser.add_argument("-d", "--distance", type=float, action="store", help="radius in km within to search, default 200.")
parser.add_argument("-c", "--cloudiness_angle", type=float, action="store",
                    help="Only supported for tas. Angle opening w.r.t. each original angle from tas to be considered as same, in order to calculate the cloudiness to each place. Default 1º. [0-12]")
required = parser.add_argument_group('required arguments')
required.add_argument("-f", "--file", type=str, help="file containing measurement data", required=True)
required.add_argument('-s', '--source', type=str, help="data source type: sqm/tas", required=True)
args = parser.parse_args()

# global latitud and longitud
lat = None
lon = None

# global dataframe for full list of light pollution sources
df = pd.DataFrame()

# global distance, default 200
distance = 200.00

# global m10 dataframe (tas)
m10 = pd.DataFrame(columns=['Mag', 'Azi', 'Cloudiness'])

# global maximum and minimum angle in search
angle_min = []
angle_max = []

# global adjacent angles from original angles in tas
adj = 0.5

# global percentile threshold, default 30%
threshold_percent = 0.3
threshold_mag = None


# Query full list of light pollution sources, including quarry, factory, greenhouse and shopping malls within Spain
def query_function():
    places = []

    # query municipalities from Wikidata
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

    # municipalities' processing
    for item in data_municipality['results']['bindings']:
        # check if the place is within the angle range
        places.append(OrderedDict({
            'Nombre': item['Municipio']['value'],
            'Tipo': 'Municipio',
            'Provincia': item['Provincia']['value'],
            'Poblacion': round(float(item['poblacion']['value']), 0),
            'lon': item['longitud']['value'],
            'lat': item['latitud']['value']}))

    # query quarries from OSM
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

    # quarries' processing
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

    # querry factories
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

    # factories processing
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

    '''
    # querry greenhouses
    overpass_query_greenhouse = """
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

    # greenhouses' processing
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

    # querry shopping malls
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

    # shopping malls' processing
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

    # store full list at global df
    global df
    df = pd.DataFrame(places)
    df.reset_index()
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})

    # save a copy to csv
    df.to_csv("light_pollution_sources.csv")


# sqm file reader
def read_file_sqm():
    # Encoding: Western Europe
    file = open(args.file, "r", encoding='iso8859_15')
    contents = file.read()
    file.close()

    # Regex: get latitude and longitude
    global lat, lon
    lat = float(str(re.findall(r'# LATITUD: (.*)', contents)[0]).replace('\t', ""))
    lon = float(str(re.findall(r'# LONGITUD: (.*)', contents)[0]).replace('\t', ""))

    # Load and process the lowest cenit readings
    # Regex: get magnitudes of m20
    m20 = str(re.findall(r'm20 = \[(.*)\]', contents)[0]).split(", ")
    for item in m20:
        item.replace(",", ".")
    m20 = np.array(m20, dtype=np.float32)

    # Get the difference between maximum and minimum
    # Regex: Get all contents between "[" and "]"
    magnitudes = re.findall(r'\[(.*)\]', contents)
    total = []
    for item in magnitudes:
        for x in item.split(", "):
            total.append(str(x).replace(",", "."))
    total = np.asfarray(total, float)
    total_range = (total.max() - total.min()).round(2)

    # Calculate the threshold
    global threshold_percent, threshold_mag
    if threshold_mag is not None:
        th = threshold_mag
    else:
        th = m20.min() + threshold_percent * total_range

    # if percentile threshold is set as 1, full angle range
    global angle_min, angle_max
    if args.threshold_percent == 1:
        angle_min.append(0)
        angle_max.append(359.99)
        return

    # If optional opening was set, just set the global, otherwise proceed to calculate them
    if args.opening is not None:
        angle_min.append(args.opening[0])
        angle_max.append(args.opening[1])
    else:
        # Angles at left and right position of the minimum value
        center_index = int(np.where(m20 == m20.min())[0])
        angle_left = float(((center_index - 1) % 12) * 30)
        angle_right = float(((center_index + 1) % 12) * 30)

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 60º, otherwise 30º
        if m20[int(angle_left / 30)] < m20[int(angle_right / 30)]:
            angle_min.append(angle_left)
            angle_max.append(float(center_index * 30))
        elif m20[int(angle_right / 30)] < m20[int(angle_left / 30)]:
            angle_min.append(float(center_index * 30))
            angle_max.append(angle_right)
        else:
            angle_min.append(angle_left)
            angle_max.append(angle_right)

        # If value at right of min is within percentile threshold and less than the angle_right, update
        # break loop if value surpass percentile threshold
        idx = int(np.where(m20 == m20.min())[0])
        for aux in range(int(idx + 1), int(idx + 13)):
            if m20[aux % 12] <= th:
                angle_max[0] = float((aux % 12) * 30)
            else:
                break

        # If value at left of min is within percentile threshold and less than the angle_left, update
        # break loop if value surpass percentile threshold
        for aux in range(idx - 1, idx - 12, -1):
            if m20[aux % 12] <= th:
                angle_min[0] = float((aux % 12) * 30)
            else:
                break

    # Continue searching from the main maximum toward right, until main minimum
    # Set start and end indexes
    start = int(((angle_max[0] + 30) % 360) / 30)
    end = int((angle_min[0] % 360) / 30)
    if start == end:
        return
    elif start > end:
        end = end + 12
    # control angle pairs with position in list
    position = 1
    valley = False
    for index in range(start, end):
        # if in "valley"
        if m20[index % 12] <= th:
            # if first entry, new angle pairs
            if len(angle_min) < (position + 1):
                valley = True
                angle_min.append(float((index % 12) * 30))
                angle_max.append(float((index % 12) * 30))
            # if still in valley
            else:
                angle_max[position] = float((index % 12) * 30)
        # if exit the valley
        elif (m20[index % 12] > th) and (valley is True):
            position = position + 1
            valley = False


# tas file reader
def read_file_tas():
    file = open(args.file, "r", encoding='iso8859_15')
    lines = file.readlines()[1:]
    file.close()
    latlon = lines[0].split()

    # get latitude and longitude from first data line
    global lat, lon
    lat_a = latlon[9].split(":")
    lon_a = latlon[10].split(":")
    lat = float(lat_a[0]) + float(lat_a[1]) / 60 + float(lat_a[2]) / 3600
    lon = float(lon_a[0]) + float(lon_a[1]) / 60 + float(lat_a[2]) / 3600

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

    # Calculate threshold
    global threshold_percent, threshold_mag
    if threshold_mag is not None:
        th = threshold_mag
    else:
        th = mag_min + threshold_percent * mag_range

    global angle_max, angle_min
    if args.threshold_percent == 1:
        angle_min.append(0)
        angle_max.append(359.99)
        return

    # If optional opening was set, just set the global, otherwise proceed to calculate them
    if args.opening is not None:
        angle_min.append(args.opening[0])
        angle_max.append(args.opening[1])
    else:
        # position of the minimum and its angle
        center_index = m10['Mag'].argmin()
        angle_center = m10.loc[[center_index]]['Azi'].item()
        # magnitudes and angles of adjacents from minimum
        mag_left = m10.loc[[(center_index - 1) % len(m10)]]['Mag'].item()
        mag_right = m10.loc[[(center_index + 1) % len(m10)]]['Mag'].item()
        angle_left = m10.loc[[(center_index - 1) % len(m10)]]['Azi'].item()
        angle_right = m10.loc[[(center_index + 1) % len(m10)]]['Azi'].item()

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 22º, otherwise 11º
        if mag_left < mag_right:
            angle_min.append(angle_left)
            angle_max.append(angle_center)
        elif mag_right < mag_left:
            angle_min.append(angle_center)
            angle_max.append(angle_right)
        else:
            angle_min.append(angle_left)
            angle_max.append(angle_right)

        max_index = center_index
        min_index = center_index
        # If value at right of min is within threshold and less than the angle_right, update
        # break loop if value surpass threshold
        for aux in range(center_index + 1, center_index + len(m10)):
            val_max = m10.loc[[aux % len(m10)]]['Mag'].item()
            if val_max <= th:
                angle_max[0] = m10.loc[[aux % len(m10)]]['Azi'].item()
                max_index = aux % len(m10)
            else:
                break

        # If value at left of min is within threshold and less than the angle_left, update
        # break loop if value surpass threshold
        for aux in range(center_index - 1, center_index - len(m10), -1):
            val_min = m10.loc[[aux % len(m10)]]['Mag'].item()
            if val_min <= th:
                angle_min[0] = m10.loc[[aux % len(m10)]]['Azi'].item()
                min_index = aux % len(m10)
            else:
                break

    # Continue searching from the main maximum toward right, until main minimum
    # Set start and end indexes
    start = (max_index + 1) % len(m10)
    end = min_index
    if start == end:
        return
    elif start > end:
        end = end + len(m10)
    # control of angle pairs with position of angle in the list
    position = 1
    valley = False
    for index in range(start, end):
        # if enter the "valley"
        if m10.loc[[index % len(m10)]]['Mag'].item() <= th:
            # if first entry, new pair of angles
            if len(angle_min) < (position + 1):
                valley = True
                angle_min.append(m10.loc[[index % len(m10)]]['Azi'].item())
                angle_max.append(m10.loc[[index % len(m10)]]['Azi'].item())
            # if still in valley
            else:
                angle_max[position] = m10.loc[[index % len(m10)]]['Azi'].item()
        # if exit the "valley"
        elif (m10.loc[[index % len(m10)]]['Mag'].item() > th) and (valley is True):
            position = position + 1
            valley = False


# Process all conditions, including distance and angle opening
def process():
    global df
    global m10
    global latitude, longitude, distance, angle_max, angle_min
    global adj

    max_a = []
    min_a = []
    # convert upper bound (0-360) into (-180, 180)
    for idx in range(0, len(angle_max)):
        if angle_max[idx] != angle_min[idx]:
            if angle_max[idx] > 180:
                max_a.append(angle_max[idx] - 360)
            else:
                max_a.append(angle_max[idx])

    # convert lower bound (0-360) into (-180, 180)
    for idx in range(0, len(angle_min)):
        if angle_min[idx] != angle_max[idx]:
            if angle_min[idx] > 180:
                min_a.append(angle_min[idx] - 360)
            else:
                min_a.append(angle_min[idx])

    # get sublist of original angles from tas within the global angle opening for tas with -n
    sublist = []
    for index, row in df.iterrows():
        # if the place is within the radius
        if float(dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km) <= distance:
            # if the place is within the angle range
            angle = bearing(lon, lat, float(row['lon']), float(row['lat']))
            cloudiness = "-"
            for pos in range(0, len(min_a)):
                if ((max_a[pos] < min_a[pos]) and (angle >= min_a[pos] or angle <= max_a[pos])) or (
                        (max_a[pos] > min_a[pos]) and (min_a[pos] <= angle <= max_a[pos])):
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
                    sublist.append(OrderedDict({
                        'Nombre': row['Nombre'],
                        'Tipo': row['Tipo'],
                        'Provincia': row['Provincia'],
                        'Poblacion': row['Poblacion'],
                        'Distancia': dist.geodesic((lat, lon), (float(row['lat']), float(row['lon']))).km,
                        'Dirección': angle,
                        'Nubosidad': cloudiness
                    }))

    result = pd.DataFrame(sublist)
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


# Automatic processing for sqm data
def auto_sqm():
    read_file_sqm()
    data = process()

    if not data.empty:
        data = data[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección"]]
        data.to_csv('result.csv')
        print('Result saved in: result.csv')
    else:
        print('No matching records found')


# Automatic processing for tas data
def auto_tas():
    read_file_tas()
    data = process()

    if not data.empty:
        data = data[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección", "Nubosidad"]]
        data.to_csv("result.csv")
        print("Result saved in: result.csv")
    else:
        print("No matching records found")


if __name__ == '__main__':
    '''
    # query all light pollution sources in Spain (Wikidata, OSM)
    # municipality, quarry, factory, greenhouse, shopping mall
    print("Initializing...")
    print("The process will take about 75 seconds.")

    start = time.time()
    query_function()
    end = time.time()
    print("Time spent: " + str(round((end - start), 2)) + "s")
    '''

    # check cloudiness angle
    if args.cloudiness_angle is not None:
        if args.source.lower() != 'tas':
            parser.error('Sorry, the cloudiness angle opening is only supported for tas')
        elif not check(args.cloudiness_angle, 0, 12):
            parser.error(
                'Please, the angle opening must be less or equal than 12 due to the spacing of original angles, otherwise would cause overlap')
        else:
            adj = args.cloudiness_angle / 2

    # check distance
    if args.distance is not None:
        distance = args.distance

    # check incompatibility between percentile threshold, magnitude threshold and angle opening
    if args.threshold_percent is not None and args.threshold_mag is not None and args.opening is not None:
        parser.error('Sorry, percentile threshold, magnitude threshold and angle opening are mutually not compatible')
    elif args.threshold_percent is not None and (args.threshold_mag is not None or args.opening is not None):
        parser.error('Sorry, percentile threshold is not compatible with magnitude threshold and/or angle opening')
    elif args.threshold_mag is not None and (args.threshold_percent is not None or args.opening is not None):
        parser.error('Sorry, magnitude threshold is not compatible with percentile threshold and/or angle opening')

    # check percentile threshold
    if args.threshold_percent is not None:
        if not 0 <= args.threshold_percent <= 1:
            parser.error('Percentile threshold error: out of bound [0.00-1.00]')
        else:
            threshold_percent = args.threshold_percent

    # check magnitude threshold
    if args.threshold_mag is not None:
        if not 0 < args.threshold_mag:
            parser.error('Magnitude threshold error: negative value')
        else:
            threshold_mag = args.threshold_mag

    # Load all light pollution sources in Spain
    df = pd.read_csv("light_pollution_sources.csv")
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})

    # check source type
    if args.source.lower() == 'sqm':
        auto_sqm()
    elif args.source.lower() == 'tas':
        auto_tas()
    else:
        parser.error('Please specify the input data type: sqm/tas')
