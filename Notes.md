Crime statistics: https://knoema.com/atlas/Cameroon/topics/Crime-Statistics
	Homicides, Theft, Burglary, Assault, Kidnapping, Rape, Robbery

Thesis:
	* https://tel.archives-ouvertes.fr
	* http://dblp.uni-trier.de/pers/hd/t/Tchuente:Maurice
	* http://www.univ-douala.com/index.php?option=com_content&view=article&id=405:theses-soutenues-par-les-enseignants-de-luniversite-de-douala-20062016&catid=46:theses-et-ouvrages
	* http://www.univ-douala.com/index.php?option=com_content&view=article&id=404%3Atheses-soutenues-dans-les-differentes-ecoles-doctorales&catid=46%3Atheses-et-ouvrages&Itemid=2
	* https://www.theses.fr/2017LYSE3005  (https://www.theses.fr/086909304)
	* http://www.univ-dschang.org/wp-content/uploads/2016/10/RepertoireThesesSoutenues-2016.pdf
	*

Maps:
- wikimapia.org
- www.citipedia.info

* À contacter

---
to:
- http://www.unmondeavenir.org/index.php/contact (done)
- Offre orange
- Redhac (done)

https://www.yammer.com/ericsson.com/threads/870249623

title:
Contribution à https://katika237.com

content:
Bonjour à vous,
Je suis TASSING Remi, software engineer. J'ai recemment lancé la plateforme https://katika237.com


--- (done)
to: Ecclésiaste Deudjui from geopolis.francetvinfo.fr
Accidents de circulation

--- (done)
to: Cameroon Association for the Defence of Victims of Accidents, CADVA,
    Fidelis Ngocha, Executive Secretary of CADVA,

to: hat is why NGOs such as the Road Safety Advocacy Network; SECUROUTE

--
monodjana2002@yahoo.fr
Dr. Godfrey Tangwa, gbtangwa@yahoo.com
MANGA BIHINA Antoine, mangabihina.uy1@yahoo.fr
MENYOMO Ernest, menyomo.ernst@yahoo.fr


*Global stats
http://camerounlink.com/actu/accidents-de-la-route-4200-morts-en-quatre-ans-/60528/0
Statistiques des accidents
Années : 2007 2008 2009 2010
Nombre d’accidents : 3277 3566 3806 3503
Nombre de blessés : 4829 4635 4019 5292
Nombre de tués : 990 1056 936 1258
Source : Gendarmerie nationale  


* Backup  
cd /tmp
sudo su -p -l postgres  
pg_dump katika -f katika-2021-05-29.dump

sudo su lapiro
pg_dump katika > /tmp/katika-2021-04-23.sql


WSGI with uwsgi
sudo su katika
source venv/bin/active
uwsgi --ini katika_uwsgi.ini


Fulltext search
https://www.enterprisedb.com/postgres-tutorials/how-implement-faceted-search-django-and-postgresql

## Update search_vector field
https://blog.lotech.org/postgres-full-text-search-with-django.html

## Unaccent

https://pretagteam.com/question/how-use-unaccent-with-full-text-search-in-django-110

ArmpEntry.objects.update(search_vector=SearchVector('title','content', config='french_unaccent'))




Context issue (older mezzanine version with django-1.11)
https://github.com/stephenmcd/mezzanine/pull/1750/commits/b2830271f20bd7ea0a914175d90029df2dcb5d5e


python3 -m pip install -U --force-reinstall pip
pip3 install mezzanine==v5.0.0-rc.1 django==3.2

pip3 install mezzanine==4.3.1 django==1.11
pip3 install django-debug-toolbar==1.9.1


django.contrib.humanize
{% load humanize %}
https://docs.djangoproject.com/en/1.11/ref/contrib/humanize/#ref-contrib-humanize

Issue with spurl toggle-query
https://github.com/j4mie/django-spurl/issues/28

work-around
#if key in current_query and first in current_query[key]
if key in current_query and first == current_query[key]:
#OR
#if key in current_query and first in current_query[key] and second not in current_query[key]:


