import folium
from folium.map import *
from folium.plugins import MarkerCluster
from folium.plugins import FloatImage
from PIL import Image


# Build interactive map showing places with their details from the result data
def mapper(data, lon, lat, type, output, indicator):
    # Create base map
    m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()])

    # generical layer
    g = folium.FeatureGroup(name='Generical', overlay=True, show=True)

    # detailed layer
    d = folium.FeatureGroup(name='Detailed', overlay=True, show=False)

    mc = MarkerCluster()

    # add reference point to both layers. Reference point refers to the place where light pollution measurements was taken
    g.add_child(folium.Marker(location=(lat, lon), popup='Reference point', icon=folium.Icon(color='black')))
    d.add_child(folium.Marker(location=(lat, lon), popup='Reference point', icon=folium.Icon(color='black')))

    # Process all places and place them into both layers of the map.
    # Marker colors: blue-Municipio, red-Fábricas, orange-CentroComercial, purple-Minas, green-Invernadero, black-reference
    for index, row in data.iterrows():
        name = row['Nombre']
        type = row['Tipo']
        population = row['Poblacion']
        distance = row['Distancia']
        if type == 'tas':
            cloudiness = row['Nubosidad']
        else:
            cloudiness = "-"
        coordinates = str(row['lat']) + ", " + str(row['lon'])

        if type == 'Municipio':
            population = int(population)
            d.add_child(folium.Marker(location=(float(row['lat']), float(row['lon'])),
                          popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Población: '
                                '</b>%s<br></br><b>Distancia: </b>%s km<br></br><b>Nubosidad: '
                                '</b>%s<br></br><b>Coordenadas: </b>%s' % (name, type, population, distance,
                                                                           cloudiness, coordinates),
                          icon=folium.Icon(color='blue')))
            mc.add_child(
                folium.Marker(location=(float(row['lat']), float(row['lon'])),
                              popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Población: '
                                    '</b>%s<br></br><b>Distancia: </b>%s km<br></br><b>Nubosidad: '
                                    '</b>%s<br></br><b>Coordenadas: </b>%s' % (name, type, population, distance,
                                                                               cloudiness, coordinates),
                              icon=folium.Icon(color='blue'))
            )
        elif type == 'Fábricas':
            d.add_child(folium.Marker(location=(float(row['lat']), float(row['lon'])),
                          popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (name, type,
                                                                                                        distance,
                                                                                                        cloudiness,
                                                                                                        coordinates),
                          icon=folium.Icon(color='red')))
            mc.add_child(
                folium.Marker(location=(float(row['lat']), float(row['lon'])),
                              popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                    '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (
                                    name, type,
                                    distance,
                                    cloudiness,
                                    coordinates),
                              icon=folium.Icon(color='red'))
            )
        elif type == 'Centro Comercial':
            d.add_child(folium.Marker(location=(float(row['lat']), float(row['lon'])),
                          popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (name, type,
                                                                                                        distance,
                                                                                                        cloudiness,
                                                                                                        coordinates),
                          icon=folium.Icon(color='orange')))
            mc.add_child(
                folium.Marker(location=(float(row['lat']), float(row['lon'])),
                              popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                    '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (
                                    name, type,
                                    distance,
                                    cloudiness,
                                    coordinates),
                              icon=folium.Icon(color='orange'))
            )
        elif type == 'Minas':
            d.add_child(folium.Marker(location=(float(row['lat']), float(row['lon'])),
                          popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (name, type,
                                                                                                        distance,
                                                                                                        cloudiness,
                                                                                                        coordinates),
                          icon=folium.Icon(color='purple')))
            mc.add_child(
                folium.Marker(location=(float(row['lat']), float(row['lon'])),
                              popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                    '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (
                                    name, type,
                                    distance,
                                    cloudiness,
                                    coordinates),
                              icon=folium.Icon(color='purple'))
            )
        elif type == 'Invernadero':
            d.add_child(folium.Marker(location=(float(row['lat']), float(row['lon'])),
                          popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (name, type,
                                                                                                        distance,
                                                                                                        cloudiness,
                                                                                                        coordinates),
                          icon=folium.Icon(color='green')))
            mc.add_child(
                folium.Marker(location=(float(row['lat']), float(row['lon'])),
                              popup='<b>Nombre: </b>%s<br></br><b>Tipo: </b>%s<br></br><b>Distancia: '
                                    '</b>%s km<br></br><b>Nubosidad: </b>%s<br></br><b>Coordenadas: </b>%s' % (
                                    name, type,
                                    distance,
                                    cloudiness,
                                    coordinates),
                              icon=folium.Icon(color='green'))
            )

    # add the MarkerCluster to generical layer
    g.add_child(mc)

    # add the generical layer to Map
    m.add_child(g)

    # add the detailed layer to Map
    m.add_child(d)

    # add indicator image to map if was set
    if indicator is not None:
        img = Image.open(indicator)
        img.putalpha(166)
        size = 250, 250
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(output + '_indicator.png')
        m.add_child(FloatImage(output + '_indicator.png', bottom=3, left=3))

    # add layer control functionality
    m.add_child(LayerControl())

    # automatic map bounds setting
    m.fit_bounds(g.get_bounds())

    # save map to "map.html"
    m.save(output + "_map.html")

    print("Map saved in: " + output + "_map.html")