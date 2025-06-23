source ~/.nvm/nvm.sh
source ~/venv/bin/activate
export DJANGO_READ_DOT_ENV_FILE=True
git pull
echo "Setting correct Node version"
nvm use
echo "Building"
npm run build


echo "Running Django build commands"
ENV=offline \
    DJANGO_SETTINGS_MODULE=config.settings.staticfiles \
    python manage.py compilescss

ENV=offline \
    DJANGO_SETTINGS_MODULE=config.settings.staticfiles \
    python manage.py collectstatic --noinput --ignore=*.scss

