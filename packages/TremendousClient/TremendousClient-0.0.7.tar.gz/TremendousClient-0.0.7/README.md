[![PyPI version](https://img.shields.io/pypi/v/TremendousClient.svg)](https://pypi.python.org/pypi/TremendousClient)

# Tremendous Api Client Python PyPackage

Tremendous Api Client client is a Python library to access services quickly.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install TremendousClient
```
## Environment Variables

```bash
TREMENDOUS_ENV: 'dev|prod'
TREMENDOUS_TOKEN: 'TREMENDOUS TOKEN'
```
### Note
If you don't want to set this variables from global environment you can pass them to class.
You can see usage below
## Usage

```python
from tremendous import TremendousService

kwargs = {
    # you can also set tremendous environment from environment.
    'environment': 'dev|prod',  # Default value : dev
    # you can also set token from environment.
    'token': 'tremendous token',  # Default value : None
}
# Initialize client with
tremendous_service = TremendousService()
# or tremendous_service = TremendousService(**kwargs)

# For Products
products = tremendous_service.getProducts()

# For Funding Source
funding_source = tremendous_service.getFundingSource()

# For Create Order
body = {
        "payment": {
            "funding_source_id": "funding_source_id"
        },
        "rewards": [
            {
                "products": [
                    "product_id"
                ],
                "value": {
                    "denomination": 2,
                    "currency_code": "USD"
                },
                "recipient": {
                    "name": "John Doe Jr.",
                    "email": "johndoe@example.com"
                },
                "delivery": {
                    "method": "LINK"
                }
            }
        ]
    }
order = tremendous_service.createOrder(body)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
