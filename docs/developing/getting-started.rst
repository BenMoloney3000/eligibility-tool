Copy example.env to .env and modify as necessary. You might need to modify the DATABASE_URL host to match the IP address of the postgres server in the container.

.. code-block:: bash

    source .env
    python3 -m venv ~/.virtualenvs/prospector
    source ~/.virtualenvs/prospector/bin/activate
    make sync
    make docker-local-up
    ./manage.py migrate
    ./manage.py createcachetable
    ./manage.py runserver

To clear the postcode cache:

.. code-block:: bash

   ./manage.py shell
   from django.core.cache import caches
   caches["postcodes"].clear()

To run the tests:

.. code-block:: bash

   pytest

To run the pre-commit hooks:

.. code-block:: bash

   pre-commit install
