#!/bin/sh

cd /opt/katika
#source venv/bin/active
venv/bin/python manage.py get_armp_entries
venv/bin/python manage.py collect_content_when_empty
venv/bin/python manage.py tender_twitter_bot
