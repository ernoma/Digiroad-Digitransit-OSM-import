
#
# This script calculates some road name Digiroad vs. OSM statistics based on
# already created list of road names that are in Digiroad but not in OSM
# (for a municipality).
#

import json
from lxml import etree
import psycopg2
from psycopg2.extensions import AsIs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("missing_names_file", help="name of the file that contains the list of the missing names previously created")
parser.add_argument("digiroad_db_table", help="name of the database table to query Digiroad data. kunnat_ita for Sipoo, kunnat_lansi for Kirkkonummi, and kunnat_keski for Helsinki, Espoo, Vantaa, and Kauniainen")
parser.add_argument("digiroad_kuntakoodi", help="code of the municipality for which data is retrieved for. 91=Helsinki, 49=Espoo, 92=Vantaa, 753=Sipoo, 257=Kirkkonummi, 235=Kauniainen")
args = parser.parse_args()

#print(args)

conn = psycopg2.connect("dbname=digiroad_test_db host=localhost port=5432 user=osm_import password=osm_import")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT tienimi_su FROM %(table)s WHERE tienimi_su!='' AND kuntakoodi=%(mun_code)s", { "table": AsIs(args.digiroad_db_table), "mun_code": args.digiroad_kuntakoodi})

digiroad_cols = cursor.fetchall()
digiroad_cols_count = len(digiroad_cols)
#print(digiroad_cols[0])

count_no_osm_match = 0
missing_road_names = []


with open(args.missing_names_file, 'r') as data_file:
    missing_road_names = json.load(data_file)
    count_no_osm_match = len(missing_road_names)
    print("Count of name cols from Digiroad:", digiroad_cols_count)
    print("Count of no matching name tag in OSM for the Digiroad tienimi_su:", count_no_osm_match)
    print("Percentage:", "%.2f" % round(count_no_osm_match / digiroad_cols_count * 100, 2), "\b%")


