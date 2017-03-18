
#
# Creates a file that contains the municipality border coordinates as
# a space sepated lat lon coordinates.
# The output is used in Overpass API queries to specify the area of interest.
#

import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("geojson_file", help="geojson file that contains Feature collection with one feature that has polygon geometry")
parser.add_argument("poly_file", help="output file that contains the lat lon coordinate pairs as space delimited list")
args = parser.parse_args()

polyString = ""

with open(args.geojson_file) as data_file:
    data = json.load(data_file)
    lines = data['features'][0]['geometry']['coordinates'][0]
    for line in lines:
        #print(line)
        polyString += str("%.9f" % round(line[1],9)) + " " + str("%.9f" % round(line[0], 9)) + " "

    #print(polyString)

with open(args.poly_file, 'w') as output_file:
    output_file.write(polyString)
    
