from io import StringIO

import geopandas as gpd
import pandas as pd

EARTHQUAKES_STR = """\
DateTime,Latitude,Longitude,Depth,Magnitude,MagType,NbStations,Gap,Distance,RMS,Source,EventID
1967/08/01 10:33:50.47,36.08000,-121.07083,80.339,2.50,Mx,10,292,42,0.25,NCSN,1000872
1967/08/02 02:49:12.55,35.63433,-120.75716,3.980,2.60,Mx,9,322,108,0.24,NCSN,1000887
1967/08/03 05:55:26.73,36.37967,-121.00850,39.609,2.70,Mx,10,298,21,0.41,NCSN,1000912
"""

EARTHQUAKES_STR_2 = """
DateTime,Latitude,Longitude,Depth,Magnitude,MagType,NbStations,Gap,Distance,RMS,Source,EventID
1967/08/03 06:57:01.25,36.39550,-121.01667,40.159,2.70,Mx,10,293,19,0.46,NCSN,1000916
1967/08/03 20:21:26.52,36.54350,-121.17216,5.945,2.60,Mx,10,132,6,0.07,NCSN,1000926
1967/08/09 04:53:59.73,35.40150,-120.58783,4.060,2.60,Mx,7,331,131,0.26,NCSN,1000979
"""

EARTHQUAKES_DF = pd.read_csv(StringIO(EARTHQUAKES_STR))

EARTHQUAKES_DF_2 = pd.read_csv(StringIO(EARTHQUAKES_STR_2))
EARTHQUAKES_GDF = gpd.GeoDataFrame(
    EARTHQUAKES_DF_2.drop(["Longitude", "Latitude"], axis=1),
    geometry=gpd.points_from_xy(EARTHQUAKES_DF_2.Longitude, EARTHQUAKES_DF_2.Latitude),
)
