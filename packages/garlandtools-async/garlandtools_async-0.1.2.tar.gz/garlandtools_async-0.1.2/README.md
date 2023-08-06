# garlandtools-py

Work in progress project to provide a async wrapper around the Garland Tools API as detailed here:
https://www.cyanclay.xyz/info/garland-tools-api-doc-en/

# Rough roadmap

- Implement search and single get
- Inteligent model system that will check the "partials" of an existing result before polling the API if the data requested is not present
- Caching layer using `cachetools` to reduce the number of queries made to the API
- Optional support for a redis cache to allow for more persistent caching

# Contributions welcome
PR's and issues welcome
