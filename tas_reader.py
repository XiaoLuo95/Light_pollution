# tas file reader
def read_tas(filename):
    file = open(filename, "r", encoding='iso8859_15')
    lines = file.readlines()[1:]
    file.close()
    firstline = lines[0].split()

    # get latitude and longitude from first data line
    lat_a = firstline[9].split(":")
    lon_a = firstline[10].split(":")
    lat = float(lat_a[0]) + float(lat_a[1]) / 60 + float(lat_a[2]) / 3600
    lon = float(lon_a[0]) + float(lon_a[1]) / 60 + float(lat_a[2]) / 3600

    return lat, lon, lines

