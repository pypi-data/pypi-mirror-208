import asyncio
from typing import Any, Coroutine, TypeVar
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, shape
from shapely import wkt, wkb
import folium
import pandas as pd
from pandas_flavor import register_dataframe_method, register_dataframe_accessor
from .connection import connection_url, query

from pandas import *
from geopandas import *


def create_marker_icon(color):
    # Define a function to create a custom marker icon
    return folium.Icon(
        color=color,
        icon="circle",
        prefix="fa"
    )


def marker(location, color='red', popup=None, tooltip=None):
    return folium.Marker(location=location, icon=create_marker_icon(color), popup=popup, tooltip=tooltip)


def read_csv(file, latitude='latitude', longitude='longitude', geometry=['geometry', 'geom'], format='', **kwargs) -> gpd.GeoDataFrame:
    csv = pd.read_csv(file, **kwargs)
    try:
        return csv.geo(latitude=latitude, longitude=longitude, geometry=geometry, format=format, **kwargs)
    except Exception as e:
        print(e)
        return csv


T = TypeVar('T')


def read_sql(sql, database=connection_url(), latitude='latitude', longitude='longitude', geometry=['geometry', 'geom', 'wkb_geometry'], format='', **kwargs) -> gpd.GeoDataFrame:
    cols, results = query(sql, database)
    sql = pd.DataFrame(results, columns=[col[0] for col in cols])
    try:
        return sql.geo(latitude=latitude, longitude=longitude, geometry=geometry, format=format, **kwargs)
    except Exception as e:
        print(e)
        return sql


@register_dataframe_accessor("geo")
class GeoDataFrameAccessor():
    def __init__(self, df):
        self._df = df

    def __call__(self, *args, **kwargs):
        self._df = create_geometry_column(self._df, *args, **kwargs)
        return gpd.GeoDataFrame(self._df, crs='EPSG:4326')


def parse_geometry(g: str):
    if g.startswith('SRID'):
        g = g.split(';')[1]
        return wkt.loads(g)
    elif g.startswith('POLYGON') or g.startswith('MULTIPOLYGON') or g.startswith('POINT'):
        return wkt.loads(g)
    elif g.startswith('{'):
        return shape(g)
    else:
        return wkb.loads(g)


format_map = {
    'geojson': shape,
    'wkt': wkt.loads,
    'wkb': wkb.loads,
    '': parse_geometry
}


def create_geometry_column(df: pd.DataFrame, format='', geometry=['geometry', 'geom', 'wkb_geometry'], latitude='latitude', longitude='longitude'):
    df = df.copy()
    if len(df) == 0:
        raise Exception('No data in Dataset to create geometry')

    if type(geometry) == str and geometry in df:
        if format in format_map:
            df.loc[:, 'geometry'] = df.loc[:,
                                           geometry].apply(format_map[format])
        else:
            df.loc[:, 'geometry'] = df.loc[:, geometry]
        return df

    for col in geometry:
        if col in df:
            if format in format_map:
                df.loc[:, 'geometry'] = df.loc[:,
                                               col].apply(format_map[format])
            else:
                df.loc[:, 'geometry'] = df.loc[:, col]
            return df

    if longitude in df and latitude in df:
        df.loc[:, longitude] = df[longitude].apply(
            lambda x: '0.0' if x == '' or x is None else x)
        df.loc[:, latitude] = df[latitude].apply(
            lambda x: '0.0' if x == '' or x is None else x)
        geom = [Point(xy) for xy in zip(
            df[longitude], df[latitude])]
        df.loc[:, 'geometry'] = geom
        return df

    if 'geometry' not in df:
        raise Exception(
            'No geometry column found in Dataset. Please provide a geometry column or a latitude and longitude column')

    return df

    # # Create a GeoDataFrame from the DataFrame
    # gdf = gpd.GeoDataFrame(df, crs='EPSG:4326')
    # return gdf


@register_dataframe_method
def map_it(df: pd.DataFrame, format='', tooltip='name', geometry=['geometry', 'geom'], map=None, color='green', zoom_level=5, center=[20.5937, 78.9629]):
    if isinstance(df, gpd.GeoDataFrame):
        gdf = df
    else:
        gdf = df.geo(format=format, geometry=geometry)

    geometry = 'geometry'

    _map = map if map is not None else folium.Map(
        location=center, zoom_start=zoom_level)
    errs = []
    # Add the points to the map
    for idx, row in gdf.iterrows():
        if not row[geometry].is_empty:

            geom = row[geometry]
            if isinstance(geom, Point):
                if tooltip in row:
                    _tooltip = row[tooltip]
                elif '{' in tooltip:
                    _tooltip = tooltip.format(**row.to_dict())
                else:
                    _tooltip = "{},{}".format(
                        row[geometry].x, row[geometry].y)
                marker(location=[row[geometry].y, row[geometry].x],
                       tooltip=_tooltip, color=color).add_to(_map)
            if isinstance(geom, Polygon) or isinstance(geom, MultiPolygon):
                if tooltip in row:
                    _tooltip = row[tooltip]
                elif '{' in tooltip:
                    _tooltip = tooltip.format(**row.to_dict())
                else:
                    _tooltip = ""
                folium.GeoJson(data=gpd.GeoSeries(
                    geom).to_json(), tooltip=_tooltip).add_to(_map)
        else:
            errs.append(idx)

    return _map
