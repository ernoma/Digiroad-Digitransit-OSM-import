
#
# This script compares Digiroad Finnish road names to OSM highway names and if
# the Digiroad road name is not found in OSM
# (in the specified municipality dataset) then
# the name is included in the list that is outputted
# to the generated JSON output file.
#

import json
from lxml import etree
import psycopg2
from psycopg2.extensions import AsIs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("municipality_osm_file", help="file containing OSM data for the area that was queried via Overpass API")
parser.add_argument("missing_names_output_json_file", help="name of the file that will contain the Finnish names from Digiroad database that did not have match as name tag for any highway tagged way in OSM for the municipality area")
parser.add_argument("digiroad_db_table", help="name of the database table to query Digiroad data. kunnat_ita for Sipoo, kunnat_lansi for Kirkkonummi, and kunnat_keski for Helsinki, Espoo, Vantaa, and Kauniainen")
parser.add_argument("digiroad_kuntakoodi", help="code of the municipality for which data is retrieved for. 91=Helsinki, 49=Espoo, 92=Vantaa, 753=Sipoo, 257=Kirkkonummi, 235=Kauniainen")
args = parser.parse_args()

#print(args)

conn = psycopg2.connect("dbname=digiroad_import_db host=localhost port=5432 user=osm_import password=osm_import")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT tienimi_su FROM %(table)s WHERE tienimi_su!='' AND kuntakoodi=%(mun_code)s", { "table": AsIs(args.digiroad_db_table), "mun_code": args.digiroad_kuntakoodi})

digiroad_cols = cursor.fetchall()
digiroad_cols_count = len(digiroad_cols)
#print(digiroad_cols[0])

count_no_osm_match = 0

missing_road_names = []

osm_xml = etree.parse(args.municipality_osm_file).getroot()

for i, digiroad_col in enumerate(digiroad_cols):

    percentage = i / digiroad_cols_count * 100
    print("Done", "%.2f" % round(percentage, 2), "\b%")

    try:
        ways = osm_xml.xpath("//way/tag[@k='name' and @v='%s']/parent::way" % digiroad_col[0])

        if(len(ways) == 0):
            if digiroad_col[0] not in missing_road_names:
                count_no_osm_match += 1
                missing_road_names.append(digiroad_col[0])
    except Exception as e:
        print(digiroad_col[0])
        print(e)
                
cursor.close()
conn.close()

print("Count of name cols from Digiroad:", digiroad_cols_count)
print("Count of no matching name tag in OSM for the Digiroad tienimi_su:", count_no_osm_match)
print("Percentage:", "%.2f" % round(count_no_osm_match / digiroad_cols_count * 100, 2), "\b%")
with open(args.missing_names_output_json_file, 'w', encoding='utf8') as output_file:
    json.dump(missing_road_names, output_file, ensure_ascii=False)
    print("Missing names output to file:", args.missing_names_output_json_file)

