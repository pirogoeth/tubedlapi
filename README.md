# tubedlapi

`tubedlapi` is a Flask application that wraps [`youtube-dl`](https://github.com/rg3/youtube-dl) to provide a simple, RESTful interface for downloading videos.

## Roadmap

- [ ] Integration and unit tests
- [ ] Dockerfile for development and production usage
- [ ] Webhooks on job completion/failure
- [ ] Test with PostgreSQL and MariaDB/MySQL(?)
- [ ] Interface for downloading completed jobs(?)

## Installation and Usage

    git clone https://github.com/pirogoeth/tubedlapi.git
    cd tubedlapi
    mkvirtualenv -p python3 tubedlapi
    pip install -r requirements.txt
    pip install -e .

    source env.example

    # For development
    tubedlapi

    # For production
    pip install gunicorn
    gunicorn tubedlapi.app:wsgi

## Demo

A short ASCIIcast of `tubedlapi` in action:

[![asciicast](https://asciinema.org/a/168904.png)](https://asciinema.org/a/168904)

### Configuration

`tubedlapi` is completely configured through environment variables.  An example configuration is included in [`env.example`](/env.example).  Settings are loaded and handled using a [Settings component](/src/tubedlapi/components/settings.py).

### Crypto Settings

As `tubedlapi` allows creating upload destinations for jobs, the (potentially secret) connection information must be stored in the database.

Encrypted storage is accomplished using [encrypted blob fields](/src/tubedlapi/model/fields.py), with `PBKDF2HMAC` for deriving an encryption secret and `ChaCha20Poly1305` for performing encryption of secrets. See [`crypto.py`](/src/tubedlapi/util/crypto.py) for implementation details.

For crypto settings, *at least* a `CRYPTO_SECRET` is required.  A `CRYPTO_SALT` is *highly recommended* unless you are using an in-memory database, in which case, it does not matter.

## API

The API is documented with OpenAPI / Swagger using the [Flasgger](https://github.com/rochacbruno/flasgger) plugin.

All API routes are in the [`tubedlapi.routes`](/src/tubedlapi/routes) package and have documentation in the route function docstrings.

To view OpenAPI documentation, start up the development server and navigate to `http://localhost:5000/apidocs`.

## Development

The entirety of this project is written in Python 3 with Flask as the web backend and Peewee as the database backend.

Setup of a development environment for `tubedlapi` should be quick and painless:

    mkvirtualenv -p python3 tubedlapi
    pip install -r requirements
    pip install -e .[develop]

`tubedlapi` also includes a [Sentry](https://getsentry.io) integration for easier debugging in dev and prod.  Talk with me and I can possibly set you up on my Sentry instance for development.

### Components

`tubedlapi` uses [`diecast`](https://github.com/pirogoeth/diecast) to provide a component and dependency injection system, which makes sharing reusable code chunks (such as the `CryptoProvider` or `Settings` components) much easier.  Check out the [`diecast` docs and examples](https://github.com/pirogoeth/diecast/blob/master/README.md) for more information.

## Contributing

Pull requests are welcomed and encouraged.  Feel free to ask questions via the issue tracker or anywhere else (such as [Gitter](https://gitter.im/pirogoeth)).

If you're submitting a PR, please install [`pre-commit`](https://github.com/pre-commit/pre-commit) and install the local git pre-commit hook to run code and style checks.

Any contributions will be greatly appreciated <3.

## License

Licensed under MIT. See [LICENSE](/LICENSE) for details.
