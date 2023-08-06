from typing import Optional, Union

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = None
try:
    from geopandas import GeoDataFrame
except ImportError:
    GeoDataFrame = None


def normalize_data(
    data: Optional[Union[str, DataFrame, GeoDataFrame]]
) -> Optional[str]:
    """Prepare user-provided data for transport to JS.

    Args:
        data: CSV/JSON String data or DataFrame to prepare for sending to Studio
    """
    if data is None:
        return None

    if isinstance(data, str):
        return data

    if GeoDataFrame is not None and isinstance(data, GeoDataFrame):
        # Reproject to 4326 if needed
        if data.crs and getattr(data.crs, "to_epsg", lambda: 0)() != 4326:
            data = data.to_crs(epsg=4326)

    return data.to_csv()
