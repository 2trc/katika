#!/bin/bash

#https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get/865569#865569
#sudo add-apt-repository -y ppa:deadsnakes/ppa

sudo apt-get update

#http://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
#https://www.qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu

##?? https://stackoverflow.com/questions/16527806/cannot-create-extension-without-superuser-role
##?? https://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
sudo apt-get install -y postgresql-9.5 \
						postgresql-9.5-postgis-2.1 \
						postgresql-server-dev-all \
						pgadmin3 \
						python3.6 \
						python3-pip \
						python3-psycopg2
						#qgis \
						#python-qgis \
						#qgis-plugin-grass \
						#unzip \
						#postgresql-9.3-postgis-scripts \
#we are using vagrant user to deal with postgres because we have the advantage
#of using X11 forwarding for pgAdmin and QGIS
#X11 su user problem
#http://unix.stackexchange.com/questions/110558/su-with-error-x11-connection-rejected-because-of-wrong-authentication

#use postgres user to 1)create postgresql vagrant user 2)grant superuser/createdb roles
sudo su - postgres -c "psql -c \"create user vagrant with superuser createdb;\""

sudo su - postgres -c "createdb -E UTF8 katika"

sudo su - postgres -c "psql katika -c \"CREATE EXTENSION postgis\""

#sudo su - postgres -c "psql -c \"create user lapiro password 'password'\""

# https://anycluster.readthedocs.io/en/latest/installconf.html
git clone https://github.com/umitanuki/kmeans-postgresql.git

cd kmeans-postgresql
make
sudo make install

sudo su - postgres -c "psql -f /usr/share/postgresql/10/extension/kmeans.sql -d katika"

sudo pip3 install -r /vagrant/requirements.txt

# https://code.djangoproject.com/ticket/20036
# django.contrib.gis.geos.error.GEOSException: Could not parse version info string "3.4.0dev-CAPI-1.8.0 r0"
# TODO edit /usr/local/lib/python3.6/dist-packages/django/contrib/gis/geos/libgeos.py


