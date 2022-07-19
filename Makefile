# Self-documenting makefile
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
#
DOCKER_LOCAL_CONF := docker-compose/local.yml

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ----------------------------------------------------------------------------

.PHONY: dev
dev: server ## Bring up the DB, run the server

.PHONY: server
server: docker-local-up ## Bring docker up and run the local server
	python manage.py createcachetable
	python manage.py runserver

.PHONY: pip-compile
pip-compile:  ## Recompile requirements file after a change
	pip-compile -q --output-file=requirements/base.txt requirements/base.in
	pip-compile -q --output-file=requirements/docs.txt requirements/docs.in
	pip-compile -q --output-file=requirements/local.txt requirements/local.in
	git diff requirements/

.PHONY: pip-upgrade
pip-upgrade:  ## Compile new requirements files with the latest pkg (make pip-upgrade pkg=...)
	pip-compile -qP $(pkg) --output-file=requirements/base.txt requirements/base.in
	pip-compile -qP $(pkg) --output-file=requirements/docs.txt requirements/docs.in
	pip-compile -qP $(pkg) --output-file=requirements/local.txt requirements/local.in
	git diff requirements/

.PHONY: pip-upgrade-all
pip-upgrade-all:  ## Compile new requirements files with latest possible versions of everything (be careful!)
	pip-compile -qU --output-file=requirements/base.txt requirements/base.in
	pip-compile -qU --output-file=requirements/docs.txt requirements/docs.in
	pip-compile -qU --output-file=requirements/local.txt requirements/local.in
	git diff requirements/

.PHONY: sync
sync:  ## Install dependencies
	pip-sync requirements/local.txt

.PHONY: docker-local-up
docker-local-up:  ## Bring up our local docker containers
	docker-compose -p prospector -f $(DOCKER_LOCAL_CONF) up  # --detach

.PHONY: docker-local-down
docker-local-down:  ## Shut down our local docker containers
	docker-compose -p prospector -f $(DOCKER_LOCAL_CONF) stop

.PHONY: docker-local-clean
docker-local-clean:  ## Clean system volumes (helpful for resetting broken databases)
	docker-compose -p prospector -f $(DOCKER_LOCAL_CONF) rm
	docker system prune --volumes -f

.PHONY: docker-dev-network
docker-dev-network:
	docker network inspect prospector || docker network create prospector

.PHONY: docker-dev-web-ip
docker-dev-web-ip:
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
		$(shell docker-compose -p prospector -f docker-compose/dev.yml ps -q web)

.PHONY: docker-dev-build
docker-dev-build: DOCKER_LOCAL_CONF=docker-compose/dev.yml 
docker-dev-build: export UID := $(shell id -u)
docker-dev-build: 
	docker-compose -p prospector -f $(DOCKER_LOCAL_CONF) build

.PHONY: docker-dev-up
docker-dev-up: DOCKER_LOCAL_CONF=docker-compose/dev.yml 
docker-dev-up: export UID := $(shell id -u)
docker-dev-up: docker-dev-network docker-local-up

.PHONY: docker-dev-down
docker-dev-down: DOCKER_LOCAL_CONF=docker-compose/dev.yml 
docker-dev-down: export UID := $(shell id -u)
docker-dev-down: docker-local-down

.PHONY: docker-dev-clean
docker-dev-clean: DOCKER_LOCAL_CONF=docker-compose/dev.yml 
docker-dev-clean: export UID := $(shell id -u)
docker-dev-clean: docker-local-clean

# docker-compose -p prospector -f docker-compose/dev.yml exec web /bin/bash

.PHONY: docker-dev-runserver
docker-dev-runserver: docker-dev-web-ip
docker-dev-runserver: 
	docker-compose -p prospector -f docker-compose/dev.yml exec web python ./manage.py runserver 0.0.0.0:8000

.PHONY: docker-dev-precommit
docker-dev-precommit: DOCKER_LOCAL_CONF=docker-compose/dev.yml 
docker-dev-precommit:
	docker-compose -p prospector -f docker-compose/dev.yml exec web pre-commit run --all

.PHONY: coverage
coverage:  ## Run tests & generate line-by-line coverage
	pytest --cov=prospector
	coverage html

.PHONY: test
test: test-python  ## Run all tests

.PHONY: test-python
test-python:  ## Run Python tests
	pytest --cov=prospector
	flake8 prospector

.PHONY: docker-build
docker-build:  ## Build the service image
	# If running in CI we have already built the image in the build stage
	if [ "${CI}" != "true" ]; then \
		docker build --tag $${SERVICE_IMAGE_TAG:-prospector:latest} . ; \
	fi

.PHONY: test-container
test-container: docker-build  ## Run tests of the built service docker image in a docker-compose environment
	docker-compose -p prospector-testing -f docker-compose/testing.yml build
	cd test-container && docker build --tag test-container:latest .
	docker-compose -p prospector-testing -f docker-compose/testing.yml up -d
	docker run --rm -i \
		--env BASE_URL='http://service:5000/' \
		--env USERNAME='test-superuser' \
		--env PASSWORD='test-superuser-password' \
		--network prospector-testing_prospector-network \
		test-container:latest
	docker-compose -p prospector-testing -f docker-compose/testing.yml down
	docker-compose -p prospector-testing -f docker-compose/testing.yml rm

.PHONY: docs
docs:  ## Build HTML docs (for other options run make in docs/)
	make -C docs/ html
	echo
	echo "URL: file://`pwd`/docs/_build/html/index.html"
