import geopy.distance as dist
from bearing import bearing
from collections import OrderedDict
import pandas as pd


# Process all conditions, including distance and angle opening
def algorithm(df, lat, lon, distance, angle_min, angle_max, adjacent, m10=None):
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
                    if m10 is not None:
                        for idx, r in m10.iterrows():
                            inf = float(r['Azi'].item() - adjacent) % 360
                            sup = float(r['Azi'].item() + adjacent) % 360
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
                        'Nubosidad': cloudiness,
                        'lon': row['lon'],
                        'lat': row['lat']
                    }))

    result = pd.DataFrame(sublist)
    if not result.empty:
        result = result.astype({'Distancia': float, 'Dirección': float})
        result = result.round({'Distancia': 2, 'Dirección': 2})
        result = result.sort_values(by='Distancia')
        result = result.reset_index()
        if m10 is not None:
            result = result[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección", "Nubosidad", "lon", "lat"]]
        else:
            result = result[["Nombre", "Tipo", "Provincia", "Poblacion", "Distancia", "Dirección", "lon", "lat"]]

    return result


# Check if a float number is within certain range
def check(original, inf, sup):
    if inf <= original <= sup:
        return True
    return False
