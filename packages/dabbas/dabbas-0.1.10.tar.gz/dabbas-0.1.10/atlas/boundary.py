from typing import Any, Callable, Coroutine, Generic, NewType, List, Optional, ParamSpec, TypeVar
from strawberry import type, interface, scalar, Private, enum
from strawberry.dataloader import DataLoader
from enum import Enum
from supabase import create_client
from shapely.geometry import shape
import pyproj
import psycopg2
import dabbas as db
from atlas.schema import Node, field
from atlas.db import boundary_supabase


@enum
class Unit(Enum):
    SQUARE_KILOMETERS = "square_kilometers"


JSON = scalar(
    NewType("JSON", object),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

GeoJSON = scalar(
    NewType("GeoJSON", object),
    description="The `GeoJSON` scalar type represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

# Boundaries

transformer = pyproj.Transformer.from_crs('EPSG:4326', 'WGS84', always_xy=True)


@type
class Geometry(Node):
    _geometry: Private[dict] = None
    _id: Private[int]
    name: str

    @property
    def uuid(self):
        return self.id()

    @property
    async def geometry_async(self):
        if self._geometry is not None:
            return self._geometry

        raise NotImplementedError

    @property
    def geometry(self):
        if self._geometry is not None:
            return self._geometry

        raise NotImplementedError

    @property
    def geoseries(self):
        return db.GeoSeries(shape(self.geometry), crs=4326)

    def _repr_html_(self):
        return self.gdf._repr_html_()

    @property
    async def geoseries_async(self) -> db.GeoSeries:
        return db.GeoSeries(shape(await self.geometry_async), crs=4326)

    @property
    async def gdf_async(self):
        return db.GeoDataFrame({"id": self.id(), "name": self.name, "geometry": await self.geoseries_async})

    @property
    def gdf(self):
        return db.GeoDataFrame({"id": self.id(), "name": self.name, "geometry":  self.geoseries})

    def map_it(self, *args, **kwargs):
        return self.gdf.map_it(*args, **kwargs)

    def plot(self, *args, **kwargs):
        return self.gdf.plot(*args, **kwargs)

    @property
    async def utm_geoseries_async(self):
        series = await self.geoseries_async
        utm_crs = series.estimate_utm_crs()
        return series.to_crs(crs=utm_crs)

    @property
    def utm_geoseries(self):
        series = self.geoseries
        utm_crs = series.estimate_utm_crs()
        return series.to_crs(crs=utm_crs)

    @field
    def properties(self) -> "Boundary":
        return self


@type
class Point(Geometry):
    pass


@type
class Boundary(Geometry):
    _area: Private[float] = None
    _centroid: Private[GeoJSON] = None

    @property
    async def geometry_async(self):
        if self._geometry is not None:
            return self._geometry

        self._geometry = await boundary_loader.load_async(self.type, self._id)
        return self._geometry

    @property
    def geometry(self):
        if self._geometry is not None:
            return self._geometry

        self._geometry = boundary_supabase.table(self.type).select('id,geom').eq(
            'id', self._id).execute().data[0]['geom']
        return self._geometry

    @field
    async def boundary(self) -> GeoJSON:
        if await self.geometry_async is None:
            raise Exception("Geometry is not defined")

        return await self.geometry_async

    @field
    def affluence(self) -> float:
        return 0

    @field(name="centroid")
    async def centroid_async(self) -> GeoJSON:
        if self._centroid is not None:
            return self._centroid

        if await self.geometry_async is None:
            raise Exception("Geometry is not defined")

        series = await self.utm_geoseries_async
        return series.centroid.to_crs(crs=4326)[0].__geo_interface__

    @field(name="area")
    async def area_async(self, unit: Optional[Unit] = Unit.SQUARE_KILOMETERS) -> float:
        if await self.geometry_async is None:
            raise Exception("Geometry is not defined")

        series = await self.utm_geoseries_async
        area_in_sq_mts = series.area[0]
        if unit == Unit.SQUARE_KILOMETERS:
            area_in_sq_kms = area_in_sq_mts / 1000000
            return area_in_sq_kms

    @property
    def area(self) -> float:
        if self.geometry is None:
            raise Exception("Geometry is not defined")

        area_in_sq_mts = self.utm_geoseries.area[0]
        area_in_sq_kms = area_in_sq_mts / 1000000
        return area_in_sq_kms

    @field
    def count(self) -> int:
        return 0

    @field
    async def bounds(self) -> List[float]:
        return (await self.utm_geometry).bounds

    @field
    def properties(self) -> "Boundary":
        return self


def get_boundary_async(table: str) -> Callable[[List[str]], Coroutine[Any, Any, List[object]]]:
    async def loader(keys):
        print(keys)
        dic = {}
        for row in boundary_supabase.table(table).select('id,geom').in_('id', keys).order('id').execute().data:
            dic[row['id']] = row['geom']
        return [dic[key] for key in keys]

    return loader


def get_boundary(table: str) -> Callable[[List[str]], List[object]]:
    def loader(keys):
        print(keys)
        dic = {}
        for row in boundary_supabase.table(table).select('id,geom').in_('id', keys).order('id').execute().data:
            dic[row['id']] = row['geom']
        return [dic[key] for key in keys]

    return loader


class BoundaryLoader:
    loaders = {}

    def load_batch(self, type: str, ids: List[int]):
        loader = get_boundary(type)
        return loader(ids)

    async def load_async(self, type, id):
        if type not in self.loaders:
            self.loaders[type] = DataLoader(
                get_boundary_async(type), max_batch_size=100)

        return await self.loaders[type].load(id)


boundary_loader = BoundaryLoader()


def load_boundaries(type: str, items: List["Boundary"]):
    return [shape(geom) for geom in boundary_loader.load_batch(type, [item._id for item in items])]


P = ParamSpec("P")
PR = ParamSpec("PR")
T = TypeVar("T")


class BoundaryDataFrame(db.GeoDataFrame, Generic[T]):
    rows: List[T] = []

    def __init__(self, data=None, *args, geometry=None, crs=4326, **kwargs):
        if len(data) > 0 and data[0]._geometry is None:
            geometry = load_boundaries(data[0].type, data)
        else:
            geometry = [row._geometry for row in data]
        super().__init__([{"uuid": row.uuid, "name": row.name} for row in data], *args, geometry=geometry,
                         crs=crs, **kwargs)

        self.rows.extend(data)
        proj_df = self.to_crs(crs=3857)
        self['boundary'] = self['geometry']
        self['area'] = proj_df.area / 10**6
        self[['min_lon', 'min_lat', 'max_lon', 'max_lat']] = self.bounds
        self['centroid'] = proj_df.centroid.to_crs(crs=4326)
        self['obj'] = data
        if geometry == 'centroid':
            self['geometry'] = self['centroid']


def from_boundaries(data, columns=['uuid', 'name'], crs=4326, geometry='boundary', **kwargs):
    geometry = load_boundaries(data[0].type, data)
    df = db.GeoDataFrame([{"uuid": row.uuid, "name": row.name} for row in data], geometry=geometry,
                         columns=columns, crs=crs, **kwargs)
    proj_df = df.to_crs(crs=3857)
    df['boundary'] = df['geometry']
    df['area'] = proj_df.area / 10**6
    df[['min_lon', 'min_lat', 'max_lon', 'max_lat']] = df.bounds
    df['centroid'] = proj_df.centroid.to_crs(crs=4326)

    if geometry == 'centroid':
        df['geometry'] = df['centroid']
    return df


def geodataframe(fn: Callable[P, List[T]]) -> Callable[P, BoundaryDataFrame[T]]:
    def wrapped(*args, **kwargs):
        return BoundaryDataFrame(fn(*args, **kwargs))
    return wrapped


def dataframe(fn: Callable[PR, List[Any]]) -> Callable[PR, db.DataFrame]:
    def wrapped(*args, **kwargs):
        return db.DataFrame(fn(*args, **kwargs))
    return wrapped
