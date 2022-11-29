#!/bin/sh

./manage.py crm --entity_definitions > prospector/apis/crm/entity_definitions.json 
./manage.py crm --option_set > prospector/apis/crm/optionsets.json 
./manage.py crm --picklists_csv > picklists.csv
