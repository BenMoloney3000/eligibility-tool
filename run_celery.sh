#!/bin/bash
export DJANGO_SETTINGS_MODULE=config.settings.production
cd /home/plymouth/prospector
source /home/plymouth/venv/bin/activate

set -a
. /home/plymouth/prospector/.env
set +a

celery -A prospector.apps.crm.celery worker --loglevel=info
