#
# This Dockerfile runs in two stages:
# 1. Build assets
# 2. Build Django container
#

# ---------------------------------------------------------------------------
# Build assets (Sass->CSS, Fancy JS->Boring JS)
# ---------------------------------------------------------------------------

FROM node:14-buster-slim as assetbuilder

WORKDIR /app
COPY ./package.json ./package-lock.json /app/
RUN npm install --production && npm cache clean --force
COPY ./gulpfile.js /app/
COPY ./prospector/static_src/ /app/prospector/static_src/
RUN make assets


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

# Install packages
# - Git is required for installing some pip packages
#   (should be commented out when not used)
# - proj-bin and gdal-bin are for GIS use
RUN apt-get update \
    && apt-get install -y --no-install-recommends git proj-bin gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements/production.txt /app/requirements/production.txt
WORKDIR /app
RUN pip install --no-cache-dir -r ./requirements/production.txt

COPY ./deploy/django/entrypoint /app/entrypoint
COPY ./deploy/django/start /app/start
RUN chmod +x /app/entrypoint /app/start

COPY . /app
COPY --from=assetbuilder /app/prospector/static_generated /app/prospector/static_generated

RUN ENV=offline \
	DJANGO_SETTINGS_MODULE=config.settings.staticfiles \
	python manage.py collectstatic --noinput

RUN chown -R django /app
ARG COMMIT_ID
RUN sed -i "s/@@__COMMIT_ID__@@/$COMMIT_ID/g" /app/config/settings/base.py
USER django

EXPOSE 5000
CMD ["/app/start"]
