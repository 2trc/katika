#!/bin/bash

#https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get/865569#865569
#sudo add-apt-repository -y ppa:deadsnakes/ppa

apt-get update
sudo apt-get update


#http://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
#https://www.qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu

##?? https://stackoverflow.com/questions/16527806/cannot-create-extension-without-superuser-role
##?? https://stackoverflow.com/questions/18696078/postgresql-error-when-trying-to-create-an-extension
apt-get install -y postgresql-10 \
						postgresql-10-postgis-2.4 \
						postgresql-server-dev-all \
						pgadmin3 \
						python3.6 \
						python3-pip \
						python3-psycopg2

#we are using vagrant user to deal with postgres because we have the advantage
#of using X11 forwarding for pgAdmin and QGIS
#X11 su user problem
#http://unix.stackexchange.com/questions/110558/su-with-error-x11-connection-rejected-because-of-wrong-authentication

#use postgres user to 1)create postgresql vagrant user 2)grant superuser/createdb roles
su - postgres -c "psql -c \"create user vagrant with superuser createdb;\""

su - vagrant -c 'createdb -E UTF8 katika'

su - vagrant -c "psql katika -c \"CREATE EXTENSION postgis\""

cd /tmp

# https://anycluster.readthedocs.io/en/latest/installconf.html
git clone https://github.com/umitanuki/kmeans-postgresql.git

cd kmeans-postgresql
make
make install

su - vagrant -c "psql -f /usr/share/postgresql/10/extension/kmeans.sql -d katika"

pip3 install -r /vagrant/requirements.txt

mkdir -p /vagrant/logs/

# https://code.djangoproject.com/ticket/20036
# django.contrib.gis.geos.error.GEOSException: Could not parse version info string "3.4.0dev-CAPI-1.8.0 r0"
# https://unix.stackexchange.com/questions/32907/what-characters-do-i-need-to-escape-when-using-sed-in-a-sh-script
sed -i 's/( r\\d.*/.*$'\''/' /usr/local/lib/python3.6/dist-packages/django/contrib/gis/geos/libgeos.py
#version_regex = re.compile(
#    r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))'
#    r'((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+).*$'
#)

su - vagrant -c "cd /vagrant && python3 manage.py makemigrations && python3 manage.py migrate"
su - vagrant -c "nohup python3.6 /vagrant/manage.py runserver 0.0.0.0:8000 &"


