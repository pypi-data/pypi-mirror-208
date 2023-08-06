# askCO: search and query records from Te Papa's collections API

This script provides an interface for getting data from the Museum of New Zealand Te Papa Tongarewa. With it, you can run searches and request individual records, which are returned as python objects.

See the [API documentation](https://data.tepapa.govt.nz/docs/) for what's available and how to construct searches.

Te Papa's API requires a registration key in the headers of each request – go to https://data.tepapa.govt.nz/docs/register.html to register. I recommend adding the API key to an environment variable called 'TE-PAPA-KEY', and then calling that from your script to pass to askCO.

## Installation
Clone this repo using `git clone`. Install the following packages:
- Requests

## Run a query
The `tryCO.py` file lays out a prepared search for a page of `Myosotis` specimen records in the `Plants` collection. It calls the API key, sets functional and query parameters, and sets up then runs the search request.

A `Search` request object uses:
- `quiet`: Can be `True` or `False`. If False, askCO prints messages to the console like the URL being requested.
- `timeout`: How long in seconds before the query times out.
- `attempts`: How many times a single query will be retried after an error like a timeout or connection error.
- `endpoint`: Which API endpoint to query. Defaults to `object` but others like `agent`, `taxon`, and `place` are available.
- `query`: The term you're searching for. If not searching for something specific, use the `*` wildcard.
- `filters`: Any filters you want to use in a list of key/value pairs. Can specify a collection to search here.
- `fields`: Cut the response down to specified fields. Leave as `None` to get the full record, or use a list of comma-separated fieldnames.
- `size`: How many results to return at once.
- `start`: Where to begin the page of results. Useful when requesting subsequent pages of a search.

The `Scroll` request object is similar, though it finds and returns all records, not just a page. It uses most of the same parameters, but not `start`. Scrolling works well with a `size` of `1000`. It can also use:
- `duration`: How long to keep the scroll query alive for on the API side. Defaults to `1` minute.
- `max_records`: How many records to retrieve, if you don't want everything.
- `sleep`: How long to wait between requests for scroll pages. Set this to `0.1` to ensure you avoid getting rate limited.

Search and scroll results are stored as a list of json objects in the `records` variable of the request object.

## Get a record
When requesting a single record, the `Resource` request object still uses:
- `api_key`
- `quiet`
- `timeout`
- `attempts`
- `endpoint`

It also takes an `irn` parameter, the specific number for that record within the endpoint. Make sure you've set the correct endpoint - /object/123456 isn't the same as /agent/123456.

The record's data is stored as a json object in the `response_text` variable of the request object.