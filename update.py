import pandas as pd
import requests
from collections import OrderedDict


# Query full list of light pollution sources, including quarry, factory, greenhouse and shopping malls within Spain
def update():
    print('The process will take about 90 seconds to complete.')
    print('Please be aware that the query endpoint is not very stable, sometimes could fail at update.')
    print('Processing...')
    places = []

    # query municipalities from Wikidata
    wikidata_url = 'https://query.wikidata.org/sparql'
    wikidata_query = '''
    SELECT DISTINCT ?Municipio ?Provincia ?poblacion ?longitud ?latitud (?municipality as ?uri) WHERE 
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
        places.append(OrderedDict({
            'Nombre': item['Municipio']['value'],
            'Tipo': 'Municipio',
            'Provincia': item['Provincia']['value'],
            'Poblacion': round(float(item['poblacion']['value']), 0),
            'lon': item['longitud']['value'],
            'lat': item['latitud']['value'],
            'uri': item['uri']['value']}))

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
                    'lat': element['center']['lat'],
                    'uri': '-'}))

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
                    'lat': element['center']['lat'],
                    'uri': '-'}))

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
                    'lat': element['center']['lat'],
                    'uri': '-'}))
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
                    'lat': element['center']['lat'],
                    'uri': '-'}))

    # store full list at df
    df = pd.DataFrame(places)
    df.reset_index()
    df = df.astype({'lon': float, 'lat': float})
    df = df.round({'lon': 4, 'lat': 4})

    # save a copy to csv
    df.to_csv("light_pollution_sources.csv")

    print('light_pollution_sources.csv was successfully updated.')