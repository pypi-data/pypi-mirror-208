[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

spei-python
===========

A library for accessing the SPEI API for python.


## Installation
Use the package manager [poetry](https://pypi.org/project/poetry/) to install.

    poetry install spei-python

## Test
Tested with [mamba](https://mamba-framework.readthedocs.io/en/latest/), install poetry dev packages and then run tests.

    poetry run make test

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Checksum Generator
This repo includes a utility to generate [firma digital aplicada](https://www.notion.so/fondeadoraroot/Algoritmo-de-Firma-e-Karpay-SPEI-02e6c25b7c5943bea054ae37c9605bdc)

```sh
python bin/generate_checksum.py bin/message.json
```
