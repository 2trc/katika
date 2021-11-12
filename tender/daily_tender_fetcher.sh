#!/bin/sh

cd /opt/katika
source venv/bin/active
python manage.py get_armp_entries
python manage.py collect_content_when_empty