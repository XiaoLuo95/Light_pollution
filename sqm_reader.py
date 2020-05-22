import re


# sqm file reader
# INPUT: filename, percentile threshold, magnitude threshold, angle opening
# OUTPUT: latitude, longitude, angles' lower and upper bounds
def read_sqm(filename):
    # Encoding: Western Europe
    file = open(filename, "r", encoding='iso8859_15')
    contents = file.read()
    file.close()

    # Regex: get latitude and longitude
    lat = float(str(re.findall(r'# LATITUD: (.*)', contents)[0]).replace('\t', ""))
    lon = float(str(re.findall(r'# LONGITUD: (.*)', contents)[0]).replace('\t', ""))

    return lat, lon, contents
