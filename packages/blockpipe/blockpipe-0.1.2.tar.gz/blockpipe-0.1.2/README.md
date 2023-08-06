# Blockpipe Client for Python

Blockpipe Client is a Python library for interacting with Blockpipe Endpoint API. It provides a simple interface for fetching data from the API and supports both single endpoint and multiple endpoints.

## Installation

Install the package using pip:

```bash
pip install blockpipe
```

## Usage

1.  Import `Client` and create a new instance:

```python

from blockpipe import Client

client = Client('<PROJECT_SLUG>', 
    environment='production', # optional
    base_url='https://app.blockpipe.io/endpoint', # optional
)
```

2.  Fetch data from the Blockpipe Endpoint API:

```python
results = client.get(['/path1', '/path2'])
```

# or with a single endpoint

```python
result = client.get('/path1')
```

3.  Use the fetched data in your application:

```python
for result in results:
    print(result['data'])

# If you only requested one endpoint, you can access the data directly:
print(result['data'])
```

## API

### `Client`

A Python class representing a Blockpipe Client instance.

Constructor:

- `project`: The project slug.
- `environment` (optional): The deployment environment. Default is `'production'`.
- `base_url` (optional): The base URL for the API. Default is `'https://app.blockpipe.io/endpoint'`.

### `get`

A method to fetch data from one or multiple Blockpipe Endpoint API paths.

Arguments:

- `endpoints`: A list of endpoint paths or a single endpoint path as a string.

Returns:

A list of data fetched from the specified endpoints, or a single data object if a single endpoint path was provided.

## Developer Notes

### Building the Package

```bash
poetry build
```

### Publishing the Package

```bash
poetry publish # OR
poetry publish --username __token__ --password [PYPI_TOKEN]
```

## License

[Apache 2.0](LICENSE)
