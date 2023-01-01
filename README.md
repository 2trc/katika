# Intro

This project hosts the source code of https://katika237.com
It is an umbrella of projects that focus show making useful data on Cameroon easily available e.g. on public contracts, tax declaration, incident with focus on the anglophone crisis and Boko haram, incarceration records focus on arbitrary and illegal arrests...

Each sub-project has (or should have) it's own README.md describing specific (non-)technical aspects around it

At its core Katika uses:
* Python and [Django](https://www.djangoproject.com/);
* Bootstrap JS/CSS is also used across projects;
* AngularJS is mainly used in the Incident project;
* Plotly is used in the Budget project.

# How to get started?
In order to get you started really quick, we have Vagrant to build an VM image packed with all the necessary dependencies, libraries, DB configuration... and even pre-populate some dummy data.
This is also a good way for us to enhance our documentation by using `Infrastructure-as-Code` methodology.

## If you never used Vagrant
If you haven't used Vagrant, do not worry. Head to https://www.vagrantup.com/ download and install it.
Then after cloning the repo, cd to the root directory and run `vagrant up`.
If everything goes well, a VM will be created, everything installed and Katika running in that VM on port 8000 which will be exposed to your host machine on port 8002.
So head to http://localhost:8002

## Troubleshooting
* To change how what port is exposed and, in general, OS stuff, check the Vagrantfile.
* To see what is installed and how the DB (Postgres) is configured, check install.sh
* To see/learn how to create dummy data, check populate_db.py
* To SSH into the VM, use `vagrant ssh`
* To destroy the VM for whatever reason, use `vagrant destroy`


# Intermediate
Once you feel comfortable and would like to start playing seriously, get yourself a bit more familiar with Django if you aren't already.
You'll probably need to create an admin user with `python3 manage.py createsuperuser`.
Then head to http://localhost:8002/admin and access the management interface. 
_Here is an area where Django really shines._


# Where do we think we need help?
* Katika runs on an extremely tight budget, so we need to squeeze capacity/resource whenever possible. Let us know or just submit proposal on optimization ideas.
* We think our UX/UI can be improved, so if you have front-end suggestions and would like to contribute, please do not hesitate
* We are OKish with full-text search using Postgres but we believe some improvements can be done
* We have a very weak coverage of unit test...not good
* Finally if you find security issues (vulnerabilities) please reach out directly to [tassingremi[at]gmail.com](mailto:tassingremi@gmail.com?subject=katika-on-github).


# Why did we go Open Source?
By giving back to the community, we hope to foster a stronger Dev ecosystem in Cameroon and perhaps also get more contributions.

# License
This code is free as in 'free beer'. It would be nice to reference the project when used but it is NOT required.




