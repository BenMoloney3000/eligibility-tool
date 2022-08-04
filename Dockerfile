
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

# Install NVM deps
RUN bash -c 'mkdir -p /usr/share/man/man{1,7}'
RUN apt-get update && apt-get upgrade -qq -y && apt-get install -y \
  curl

# Install custom NVM/Node
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR

# NVM: v0.38.0 (latest):
# https://github.com/nvm-sh/nvm/releases
ENV NVM_VERSION v0.38.0
# NODE v14 (Active LTS) EOL 2023-04-30:
# https://nodejs.org/en/about/releases/
ENV NODE_VERSION 14.13.1

WORKDIR /app

# install.sh will automatically install NodeJS based on the presence of $NODE_VERSION
RUN curl -f -o- https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash
RUN [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"   
RUN bash -c "source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default"

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN node -v
RUN npm -v


# Requirements are installed here to ensure they will be cached.
COPY ./requirements/base.txt /app/requirements/base.txt
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
    python manage.py compilescss

RUN ENV=offline \
    DJANGO_SETTINGS_MODULE=config.settings.staticfiles \
    python manage.py collectstatic --noinput --ignore=*.scss

RUN chown -R django /app
ARG COMMIT_ID
RUN sed -i "s/@@__COMMIT_ID__@@/$COMMIT_ID/g" /app/config/settings/base.py

USER django
EXPOSE 5000
