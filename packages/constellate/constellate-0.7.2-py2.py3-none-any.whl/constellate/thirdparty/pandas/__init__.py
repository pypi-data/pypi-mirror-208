from constellate.package.package import package_available

if not package_available("pandas"):
    import logging

    _log = logging.getLogger(__name__)
    _log.warning("pandas not installed. constellate.thirdparty.pandas sub package must not be used")
else:
    #
    # Usage:
    # - Import this module as constellate.thirdparty.pandas as pd
    #
    import pandas as pd
    from pandas import *

    # (Force) pandas api extensions import
    from constellate.thirdparty.pandas.accessor.attribute_accessor import (
        DataFrameAttributeAccessor,
        SeriesAttributeAccessor,
    )
