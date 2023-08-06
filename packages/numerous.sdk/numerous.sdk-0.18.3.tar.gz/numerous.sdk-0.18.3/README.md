# numerous SDK

![pipeline](https://gitlab.com/numerous/numerous.sdk/badges/main/pipeline.svg)
![coverage](https://gitlab.com/numerous/numerous.sdk/badges/main/coverage.svg?job=pytest)
![Documentation Status](https://readthedocs.org/projects/numeroussdk/badge/?version=latest)

Welcome to the repository for `numerous.sdk`!

The `numerous.sdk` which includes all the things you need to build tools and
applications that can run on the [numerous platform](https://numerous.com).

## Dependencies

* This project requires python version 3.9 or later.

* Some dependencies are currently hosted on a pypi registry managed by the
  numerous platform team, which exists at https://pypi.numerously.com/simple.

  In the installation section below, we will show how to specify this, in order
  to properly install `numerous.sdk`.

## Installation

Some dependencies are hosted on the pypi registry
https://pypi.numerously.com/simple, which means that to install `numerous.sdk`
you must either:

1. Set the `PIP_EXTRA_INDEX_URL` environment variable
   ```
   export PIP_EXTRA_INDEX_URL="https://pypi.numerously.com/simple"
   pip install numerous.sdk
   ```
2. Use the `pip` flag `--extra-index-url`
   ```
   pip install --extra-index-url=https://pypi.numerously.com/simple numerous.sdk
   ```
3. Or add the pip flag to your `requirements.txt`, resulting in a file like
   below:
   ```
   --extra-index-url=https://pypi.numerously.com/simple
   numerous.sdk
   other_package
   ```
   which you can then install with
   ```
   pip install -r requirements.txt
   ```


## Documentation

Documentation for the numerous SDK can be found at
[readthedocs.io](https://numeroussdk.readthedocs.io). This contains the latest
documentation. We are continuously adding more, as the project matures.

## Contributing

We welcome contributions, but please read [CONTRIBUTING.md](CONTRIBUTING.md)
before you start. It lays down the processes and expectations of contributions
to the numerous SDK.

## Changes

See the [CHANGELOG.md](CHANGELOG.md) to get an overview latest features, fixes
and other changes to `numerous.sdk`, and also to find the general history of
changes.

## License

`numerous.sdk` is licensed under the MIT License, and it can be read in
[LICENSE.md](LICENSE.txt).
