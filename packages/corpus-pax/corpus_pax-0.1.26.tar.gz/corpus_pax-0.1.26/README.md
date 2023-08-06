# corpus-pax

![Github CI](https://github.com/justmars/corpus-pax/actions/workflows/main.yml/badge.svg)

Using Github API (to pull individuals, orgs, and article content), setup a local sqlite database, syncing images to Cloudflarel utilized in the [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/corpus-pax).

## Development

Checkout code, create a new virtual environment:

```sh
poetry add corpus-pax # python -m pip install corpus-pax
poetry update # install dependencies
poetry shell
```

Run tests:

```sh
pytest
```
