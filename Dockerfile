# ---------------------------------------------------------------------------
# Django container build
# ---------------------------------------------------------------------------

# We're using "Slim" (which is a cut down Debian Stretch) because Debian is a
# much more standard setup than alpine with the potential for a lot less faff
# later on if we need to install more obscure dependencies.
FROM python:3.10-slim as runtime

# Don't buffer output - we should always get error messages this way
ENV PYTHONUNBUFFERED 1

# Don't write bytecode to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Set up our user
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements/base.txt /app/requirements/base.txt
WORKDIR /app
RUN pip install --no-cache-dir -r ./requirements/base.txt

COPY \
    docker/migrate \
    docker/rqscheduler \
    docker/rqworker \
    docker/webserver \
    ./
RUN chmod +x /app/migrate /app/rqscheduler /app/rqworker /app/webserver

COPY . /app

RUN ENV=offline \
    DJANGO_SETTINGS_MODULE=config.settings.staticfiles \
    python manage.py collectstatic --noinput

RUN chown -R django /app
ARG COMMIT_ID
RUN sed -i "s/@@__COMMIT_ID__@@/$COMMIT_ID/g" /app/config/settings/base.py

USER django
EXPOSE 5000
