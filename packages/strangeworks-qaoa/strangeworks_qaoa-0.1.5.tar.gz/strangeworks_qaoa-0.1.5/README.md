![Tests](https://github.com/strangeworks/strangeworks-qaoa/actions/workflows/cron_test.yml/badge.svg)

# Strangeworks QAOA SDK Extension

This extension provides access to the Strangeworks QAOA service through the SDK.

## Installation

Install using `poetry`

```
pip install poetry
poetry install
```

## Tests

Test using pytest

```
poetry run pytest tests
```

## Lint

Lint with black

```
poetry run black .
```

## Bump version

Bump version with [poetry](https://python-poetry.org/docs/cli/#version).

```
poetry version [patch, minor, major]
```

## Update packages

Update <package> version

```
poetry update <package>
```

Update all packages

```
poetry update
```
