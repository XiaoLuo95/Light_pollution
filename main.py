import argparse
import pandas as pd
import time
from update import update
from sqm_reader import read_sqm
from tas_reader import read_tas
from sqm_angles import sqm_angles
from tas_angles import tas_angles
from filter_algorithm import algorithm
from filter_algorithm import check
from mapper import mapper

# command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold_percent", metavar='\b', type=float, action="store",
                    help="percentage of magnitude from minimum to consider. Default 0.3. Incompatible with {-T, -o}. [0.00-1.00]")
parser.add_argument("-T", "--threshold_mag", metavar='\b', type=float, action="store",
                    help="maximum real magnitude under consideration. Incompatible with {-t, -o}.")
parser.add_argument("-o", "--opening", metavar='\b', type=float, nargs=2, action="store",
                    help="angle opening's lower and upper bound, separated by whitespace. Incompatible with {-t, -T}. [0-359.99] [0-359.99]")
parser.add_argument("-d", "--distance", metavar='\b', type=float, action="store", help="radius in km within to search, default 120.")
parser.add_argument("-c", "--cloudiness_angle", metavar='\b', type=float, action="store",
                    help="Only supported for tas. Angle opening w.r.t. each original angle from tas to be considered as same, in order to calculate the cloudiness to each place. Default 1º. [0-12]")
parser.add_argument("-S", "--single", metavar='\b', type=bool, action="store", help="Default False. Angle opening for single valley of lowest value. Compatible with percentile and magnitude thresholds")
parser.add_argument("-save", "--save", metavar='\b', type=str, action="store", help="Output file name. Will apply to both data and map files.")
parser.add_argument("-i", "--indicator", metavar='\b', type=str, action="store", help="Light pollution indicator image filename. If set, the indicator will be included in the map generated.")
parser.add_argument("-u", "--update", metavar='\b', type=bool, action="store",
                    help="default False. If set as True, the script will proceed to update the list of light pollution sources in Spain.")
required = parser.add_argument_group('required arguments')
required.add_argument("-f", "--file", metavar='\b', type=str, help="file containing measurement data", required=True)
required.add_argument('-s', '--source', metavar='\b', type=str, help="data source type: sqm/tas", required=True)
args = parser.parse_args()

# global latitude and longitude
lat = None
lon = None

# global pandas dataframe for full list of light pollution sources
df = pd.DataFrame()

# global pandas dataframe for sqm and tas data
sqm = pd.DataFrame()
tas = pd.DataFrame()

# global distance, default 120km
distance = 120.00

# global m10 dataframe (tas)
m10 = pd.DataFrame(columns=['Mag', 'Azi', 'Cloudiness'])

# global maximum and minimum azimuthal angles to search
angle_min = []
angle_max = []

# global adjacent angles from original angles in tas
adjacent = 0.5

# global percentile threshold, default 30%
threshold_percent = 0.3
threshold_mag = None

# global single statement
single = False

# global output filename
output = "result"

# light pollution indicator image filename
indicator = None


# Automatic processing for sqm data
def auto_sqm():
    global sqm
    global lat, lon, angle_min, angle_max
    global threshold_percent, threshold_mag
    global single, output

    lat, lon, sqm = read_sqm(args.file)
    angle_min, angle_max = sqm_angles(sqm, threshold_percent, threshold_mag, args.opening, single)
    print(angle_min, angle_max)
    result = algorithm(df, lat, lon, distance, angle_min, angle_max, adjacent)
    mapper(result, lon, lat, "sqm", output, indicator)

    if not result.empty:
        result.to_csv(output + '.csv', index=False)
        print('Result saved in: ' + output + '.csv')

    else:
        print('No matching records found')


# Automatic processing for tas data
def auto_tas():
    global tas
    global lat, lon, angle_min, angle_max, distance
    global threshold_percent, threshold_mag, adjacent
    global single, output
    global m10

    lat, lon, tas = read_tas(args.file)
    angle_min, angle_max, m10 = tas_angles(tas, threshold_percent, threshold_mag, args.opening, m10, single)
    result = algorithm(df, lat, lon, distance, angle_min, angle_max, adjacent, m10)
    mapper(result, lon, lat, "tas", output, indicator)

    if not result.empty:
        result.to_csv(output + '.csv', index=False)
        print("Result saved in: " + output + ".csv")
    else:
        print("No matching records found")


if __name__ == '__main__':

    # If update requested, proceed to make new query
    # Otherwise data processing
    if args.update is not None:
        if args.update is True:
            # query all light pollution sources in Spain (Wikidata, OSM)
            # municipality, quarry, factory, greenhouse, shopping mall
            start = time.time()
            update()
            end = time.time()
            print("Time spent: " + str(round((end - start), 2)) + "s")
    else:
        # check cloudiness angle opening to consider
        if args.cloudiness_angle is not None:
            if args.source.lower() != 'tas':
                parser.error('Sorry, the cloudiness angle opening is only supported for tas')
            elif not check(args.cloudiness_angle, 0, 12):
                parser.error(
                    'Please, the angle opening must be less or equal than 12 due to the spacing of original angles, otherwise would cause overlap')
            else:
                # Single side cloudiness adjacent angle to consider
                adjacent = args.cloudiness_angle / 2

        if args.single is not None:
            if args.opening is not None:
                parser.error('Sorry, single angle opening option not supported for manual angle openings.')
            else:
                single = args.single

        # check if custom distance was set, default 200km
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

        # check output filename
        if args.save is not None:
            output = args.save

        if args.indicator is not None:
            indicator = args.indicator

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
