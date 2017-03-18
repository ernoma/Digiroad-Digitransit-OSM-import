
#
# This script is for creating a json file that
# contains such Digiroad road names that
# can be found in OSM and have Swedish name both in Digiroad and OSM but
# the Swedish names do not match.
#

import json
from lxml import etree
import psycopg2
from psycopg2.extensions import AsIs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("municipality_osm_file", help="file containing OSM data for the area that was queried via Overpass API")
parser.add_argument("missmatch_names_output_json_file", help="name of file that will contain the Digiroad database and OSM entries that have the same Finnish name but diffrent Swedish name for the municipality area")
parser.add_argument("digiroad_db_table", help="name of the database table to query Digiroad data. kunnat_ita for Sipoo, kunnat_lansi for Kirkkonummi, and kunnat_keski for Helsinki, Espoo, Vantaa, and Kauniainen")
parser.add_argument("digiroad_kuntakoodi", help="code of the municipality for which data is retrieved for. 91=Helsinki, 49=Espoo, 92=Vantaa, 753=Sipoo, 257=Kirkkonummi, 235=Kauniainen")
args = parser.parse_args()

#print(args)
#print(args.digiroad_db_table)

conn = psycopg2.connect("dbname=digiroad_test_db host=localhost port=5432 user=osm_import password=osm_import")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT tienimi_su, tienimi_ru, muokkauspv FROM %(table)s WHERE tienimi_su!='' AND tienimi_ru!='' AND kuntakoodi=%(mun_code)s ORDER BY tienimi_su", { "table": AsIs(args.digiroad_db_table), "mun_code": args.digiroad_kuntakoodi})

digiroad_cols = cursor.fetchall()
digiroad_cols_count = len(digiroad_cols)
#print(digiroad_cols[0])

osm_xml = etree.parse(args.municipality_osm_file).getroot()

missmatches = []

for i, digiroad_col in enumerate(digiroad_cols):    
    percentage = i / digiroad_cols_count * 100
    print("Done", "%.2f" % round(percentage, 2), "\b%")

    if len(missmatches) == 0 or missmatches[-1]['name'] != digiroad_col[0]:        
        try:
            ways = osm_xml.xpath("//way/tag[@k='name' and @v='%s']/parent::way" % digiroad_col[0])

            missmatch = {}
            missmatch['name'] = digiroad_col[0]
            missmatch['tienimi_ru'] = digiroad_col[1]
            missmatch['muokkauspv_dr'] = []
            missmatch['muokkauspv_dr'].append(digiroad_col[2])
            missmatch['osm_ways'] = []
                    
            for way in ways:
                #print(way.attrib)
                tags = way.xpath("tag[@k='name:sv']")
                #print(len(tags))
                if len(tags) == 1:
                    #print("found name:sv tag")
                    name_sv = tags[0].xpath("string(@v)")
                    if name_sv != digiroad_col[1]:
                        osm_way = {}
                        osm_way['name_sv_osm'] = name_sv
                        osm_way['osm_timestamp'] = way.xpath("string(@timestamp)")
                        osm_way['osm_id'] = way.xpath("string(@id)")
                        missmatch['osm_ways'].append(osm_way)

            if len(missmatch['osm_ways']) > 0:    
                missmatches.append(missmatch)
                
        except Exception as e:
            print(digiroad_col[0])
            print(e)
            
    elif missmatches[-1]['name'] == digiroad_col[0]:
        missmatches[-1]['muokkauspv_dr'].append(digiroad_col[2])
                
cursor.close()
conn.close()

with open(args.missmatch_names_output_json_file, 'w', encoding='utf8') as output_file:
    json.dump(missmatches, output_file, ensure_ascii=False)
    print("Missmatches output to file:", args.missmatch_names_output_json_file)

