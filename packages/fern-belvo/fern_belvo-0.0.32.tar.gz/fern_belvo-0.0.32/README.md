
# Belvo Python Library

[![pypi](https://img.shields.io/pypi/v/fern-belvo.svg)](https://pypi.python.org/pypi/fern-belvo)
[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)

## Documentation

API documentation is available at [here](https://developers.belvo.com/reference/using-the-api-reference).

## Installation

```bash
pip install fern-belvo
# or
poetry add fern-belvo
```

## Usage

```python
import belvo
from belvo.client import Belvo

belvo_client = Belvo(
    secret_id="YOUR_SECRET_ID",
    secret_password="YOUR_SECRET_PASSWORD",
)

link = belvo_client.links.register_link(
    institution="banamex_mx_retail",
    username="username",
    password="password",
    accessMode=belvo.EnumLinkAccessModeRequest.SINGLE,
    credentialsStorage="30d",
)

print(link)
```

## Async client

This SDK also includes an async client, which supports the `await` syntax:

```python
import asyncio
from belvo.client import AsyncBelvo

belvo_client = AsyncBelvo(
    secret_id="YOUR_SECRET_ID",
    secret_password="YOUR_SECRET_PASSWORD",
)

async def get_link() -> None:
    link = await belvo_client.links.register_link({
        institution="banamex_mx_retail",
        username="username",
        password="password",
        accessMode=belvo.EnumLinkAccessModeRequest.SINGLE,
        credentialsStorage="30d,
    })

    print(link)

asyncio.run(get_link())
```

## Sample app

To play around with the SDK in a full project, check out the [sample app](https://github.com/fern-belvo/belvo-python-sample-app).

## Beta status

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning the package version to a specific version in your pyproject.toml file. This way, you can install the same version each time without breaking changes unless you are intentionally looking for the latest version.

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically. Additions made directly to this library would have to be moved over to our generation code, otherwise they would be overwritten upon the next generated release. Feel free to open a PR as a proof of concept, but know that we will not be able to merge it as-is. We suggest opening an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
