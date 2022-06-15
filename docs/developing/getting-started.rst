Copy example.env to .env and modify as necessary. You might need to modify the DATABASE_URL host to match the IP address of the postgres server in the container.

.. code:: bash
    source .env
    python3 -m venv ~/.virtualenvs/prospector
    source ~/.virtualenvs/prospector/bin/activate
    make sync
    make docker-local-up
    ./manage.py migrate
    ./manage.py createcachetable
    ./manage.py runserver
