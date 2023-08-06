# ComboCurve client for Python

## Authorization

`combocurve_api` requires the API key and service account provided by ComboCurve, as shown in the example below:

```python
from combocurve_api_v1 import ServiceAccount, ComboCurveAuth

# Use this to create your service account manually
service_account = ServiceAccount(
    client_email='YOUR_CLIENT_EMAIL',
    client_id='YOUR_CLIENT_ID',
    private_key='YOUR_PRIVATE_KEY',
    private_key_id='YOUR_PRIVATE_KEY_id'
)
# Or use this to load it from a JSON file
# service_account = ServiceAccount.from_file("PATH_TO_JSON_FILE")

# Set your API key
api_key = 'YOUR_API_KEY'

combocurve_auth = ComboCurveAuth(service_account, api_key)

# Get auth headers
auth_headers = combocurve_auth.get_auth_headers()
```

`combocurve_auth.get_auth_headers()` should be called before every request so that the token can be
refreshed if it's about to expire. After getting the authentication headers, they can be used with any HTTP client
library. Below is an example using the [Requests](https://docs.python-requests.org) library:

```python
import requests

data = [{
    'wellName': 'well 1',
    'dataSource': 'internal',
    'chosenID': '1234'
}, {
    'wellName': 'well 2',
    'dataSource': 'internal',
    'chosenID': '4321'
}]
auth_headers = combocurve_auth.get_auth_headers()
url = 'https://api.combocurve.com/v1/wells'

response = requests.put(url, headers=auth_headers, json=data)
print(response.json())
```

## Content-Type

The ComboCurve API only accepts data serialized as JSON and the `Content-Type` header must be `application/json`. Luckily, [Requests](https://docs.python-requests.org) will take care of both things when the data is passed using the `json` parameter, as you saw in the example above. Using the `data` parameter would be less convenient but it works too:

```python
import json

response = requests.put(url,
                        headers={
                            **auth_headers, 'Content-Type': 'application/json'
                        },
                        data=json.dumps(data))
```

More information here: https://docs.python-requests.org/en/latest/user/quickstart/#more-complicated-post-requests

## Pagination

When the number of records to be returned for a request is larger than the maximum number of records that can be retrieved in a single response, the requester will need to "paginate", i.e., make multiple requests while there are more records to be returned.

This package provides a helper to assist with that. It parses the response headers and returns a new URL for the next request, if another request is needed. See this example using the [Requests](https://docs.python-requests.org) library:

```python
from combocurve_api_v1.pagination import get_next_page_url

# See Authorization section
auth_headers = combocurve_auth.get_auth_headers()

# Additional filters are allowed, it is preferred not specify skip if its value is 0
url = 'https://api.combocurve.com/v1/wells?take=200'

# First request
has_more = True

# Keep fetching while there are more records to be returned
while has_more:
    response = requests.get(url, headers=headers)

    # Process response

    url = get_next_page_url(response.headers)
    has_more = url is not None
```
