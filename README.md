# Retrofit Eligibility Web Tool

This repository contains a Django application used to assess property eligibility for retrofit measures. It exposes a REST API and a small JavaScript front end served via webpack.

## Getting Started

1. Copy `example.env` to `.env` and adjust any environment variables.
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install JavaScript dependencies:

```bash
npm install
```

4. Apply database migrations and start the development server:

```bash
./manage.py migrate
./manage.py runserver
```

See `docs/developing/getting-started.rst` for full setup instructions.

## Running Tests

Backend tests use `pytest` with settings from `config.settings.test`:

```bash
pytest
```

Front end tests can be run with:

```bash
npm test
```

## Building Documentation

Documentation lives in the `docs/` directory. Build the HTML pages with:

```bash
make -C docs html
```


