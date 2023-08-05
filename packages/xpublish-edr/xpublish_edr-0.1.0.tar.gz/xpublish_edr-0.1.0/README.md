## xpublish-edr

[![Tests](https://github.com/gulfofmaine/xpublish-edr/actions/workflows/tests.yml/badge.svg)](https://github.com/gulfofmaine/xpublish-edr/actions/workflows/tests.yml)

[Xpublish](https://xpublish.readthedocs.io/en/latest/) routers for the [OGC EDR API](https://ogcapi.ogc.org/edr/).

### Documentation and code

URLs for the docs and code.

### Installation

For `conda` users you can

```shell
conda install --channel conda-forge xpublish_edr
```

or, if you are a `pip` users

```shell
pip install xpublish_edr
```

### Example

```python
import xarray as xr
import xpublish
from xpublish.routers import base_router, zarr_router
from xpublish_edr.cf_edr_router import cf_edr_router


ds = xr.open_dataset("dataset.nc")

rest = xpublish.Rest(
    datasets,
    routers=[
        (base_router, {"tags": ["info"]}),
        (cf_edr_router, {"tags": ["edr"], "prefix": "/edr"}),
        (zarr_router, {"tags": ["zarr"], "prefix": "/zarr"}),
    ],
)
```


## Get in touch

Report bugs, suggest features or view the source code on [GitHub](https://github.com/gulfofmaine/xpublish-edr/issues).


## License and copyright

xpublish-edr is licensed under BSD 3-Clause "New" or "Revised" License (BSD-3-Clause).

Development occurs on GitHub at <https://github.com/gulfofmaine/xpublish-edr/issues>.
