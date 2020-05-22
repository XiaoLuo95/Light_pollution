import math


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