# Seam Python Library

[![pypi](https://img.shields.io/pypi/v/fern-seam.svg)](https://pypi.python.org/pypi/fern-seam)
[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)

## Documentation

API documentation is available at https://docs.seam.co/latest/api-clients/overview.

## Installation

Add this dependency to your project's build file:

```bash
pip install fern-seam
# or
poetry add fern-seam
```

## Usage

```python
from seam.client import Seam

seam_client = Seam(token="MY_TOKEN")

response = seam_client.access_codes.update_and_wait_until_ready(
    access_code_id="my access code id",
    name="access code name",
    code="access code",
    starts_at=dt.datetime(2023, 3, 1, 12, 0, 0),
    ends_at=dt.datetime(2023, 3, 5, 12, 0, 0),
)

print(response.access_code_id)
```

## Async client

This SDK also includes an async client, which supports the `await` syntax:

```python
from seam.client import AsyncSeam

seam_client = AsyncSeam(token="MY_TOKEN")

async def update_access_code() -> None:
    response = seam_client.access_codes.update_and_wait_until_ready(
        access_code_id="my access code id",
        name="access code name",
        code="access code",
        starts_at=dt.datetime(2023, 3, 1, 12, 0, 0),
        ends_at=dt.datetime(2023, 3, 5, 12, 0, 0),
    )

    print(response.access_code_id)

asyncio.run(update_access_code())
```

## Beta status

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning the package version to a specific version in your pyproject.toml file. This way, you can install the same version each time without breaking changes unless you are intentionally looking for the latest version.

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically. Additions made directly to this library would have to be moved over to our generation code, otherwise they would be overwritten upon the next generated release. Feel free to open a PR as a proof of concept, but know that we will not be able to merge it as-is. We suggest opening an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
