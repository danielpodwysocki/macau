#!/bin/bash

if [ ! -f /django/macau/init_done ]; then
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('$1', '$2', '$3')" | python /django/macau/manage.py shell  
	touch /django/macau/init_done
fi
apachectl -D FOREGROUND
