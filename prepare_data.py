
#
# This script creates OSM file on JOSM format that contains the Swedish names that are to be added to OSM database from
# the Digiroad database.
#

import datetime
from lxml import etree
import psycopg2
from psycopg2.extensions import AsIs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("municipality_osm_file", help="file containing OSM data for the area that was queried via Overpass API")
parser.add_argument("output_osm_file", help="name of the file that will contain modified OSM data in JOSM format")
parser.add_argument("digiroad_db_table", help="name of the database table to query Digiroad data. kunnat_ita for Sipoo, kunnat_lansi for Kirkkonummi, and kunnat_keski for Helsinki, Espoo, Vantaa, and Kauniainen")
parser.add_argument("digiroad_kuntakoodi", help="code of the municipality for which data is retrieved for. 91=Helsinki, 49=Espoo, 92=Vantaa, 753=Sipoo, 257=Kirkkonummi, 235=Kauniainen")
args = parser.parse_args()

#print(args)

conn = psycopg2.connect("dbname=digiroad_import_db host=localhost port=5432 user=osm_import password=osm_import")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT tienimi_su,tienimi_ru FROM %(table)s WHERE tienimi_su!='' AND tienimi_ru!='' AND kuntakoodi=%(mun_code)s", { "table": AsIs(args.digiroad_db_table), "mun_code": args.digiroad_kuntakoodi})

digiroad_cols = cursor.fetchall()
digiroad_cols_count = len(digiroad_cols)
print("Count of name cols from Digiroad: ", digiroad_cols_count)
#print(digiroad_cols[0])

osm_xml = etree.parse(args.municipality_osm_file).getroot()

for i, digiroad_col in enumerate(digiroad_cols):

    percentage = i / digiroad_cols_count * 100
    print("Done", "%.2f" % round(percentage, 2), "\b%")

    try:
        ways = osm_xml.xpath("//way/tag[@k='name' and @v='%s']/parent::way" % digiroad_col[0])
        #print(len(ways))
        #print(ways[0].tag)
        #print(ways[0].attrib)
        for way in ways:
            way.set("action", "modify")
            tag = etree.Element("tag", k="name:sv", v=digiroad_col[1])
            way.append(tag)
            tag = etree.Element("tag", k="source:name:sv", v="Digiroad.fi")
            way.append(tag)
            #tag = etree.Element("tag", k="source:name:sv:date", v=str(datetime.date.today()))
            #way.append(tag)
    except Exception as e:
        print(digiroad_col[0])
        print(e)

cursor.close()
conn.close()

mod_osm_xml_string = etree.tostring(osm_xml, pretty_print=True, encoding="UTF-8", xml_declaration=True).decode()
#print(mod_osm_xml_string)
with open(args.output_osm_file, 'w', encoding='utf8') as output_osm_file:
    output_osm_file.write(mod_osm_xml_string)
