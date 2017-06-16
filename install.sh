#!/bin/bash

sudo apt-get update

#http://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
#https://www.qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu

##?? https://stackoverflow.com/questions/16527806/cannot-create-extension-without-superuser-role
##?? https://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
sudo apt-get install -y postgresql-9.3 \
						postgresql-9.3-postgis-2.1 \
						#qgis \
						#python-qgis \
						#qgis-plugin-grass \
						#unzip \
						postgresql-9.3-postgis-scripts \
						pgadmin3 \
						python3-pip

#we are using vagrant user to deal with postgres because we have the advantage
#of using X11 forwarding for pgAdmin and QGIS
#X11 su user problem
#http://unix.stackexchange.com/questions/110558/su-with-error-x11-connection-rejected-because-of-wrong-authentication

#use postgres user to 1)create postgresql vagrant user 2)grant superuser/createdb roles
sudo su - postgres -c "psql -c \"create user vagrant with superuser createdb;\""

sudo su - vagrant -c "createdb -E UTF8 katika"

sudo su - vagrant -c "psql katika -c \"CREATE EXTENSION postgis\""

#download nyc shape file
#if [ ! -f new_york_highway.shp ]; then
# 	wget http://www.mapcruzin.com/download-shapefile/us/new_york_highway.zip
# 	unzip new_york_highway.zip
# 	sudo su - vagrant -c "shp2pgsql -c -D -s 4269 -I new_york_highway.shp |psql -d nyc"
#fi

#http://www.mapcruzin.com/free-united-states-shapefiles/free-new-york-arcgis-maps-shapefiles.htm
#importing shape file
#http://postgis.net/docs/manual-2.2/using_postgis_dbmanagement.html#loading_geometry_data


#sample queries
#
#select ST_AsText(geom),* from new_york_highway limit 20;
#select type, count(type) as num from new_york_highway group by type;

#Find intersection in a polygon/triangle somewhere around NYC-Manhattan
#select name, type,oneway
#from new_york_highway 
#where ST_Intersects(geom, ST_GeomFromText('POLYGON((-73.968890 40.769531, -73.960991 40.767752, -73.965609 40.764638, -73.968890 40.769531))', 4269))
#limit 20;

sudo pip install virtualenv

virtualenv venv -p /usr/bin/python3

source venv/bin/activate

pip install -r requirements.txt
