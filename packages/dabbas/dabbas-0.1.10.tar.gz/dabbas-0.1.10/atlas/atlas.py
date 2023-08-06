from typing import Callable, Coroutine, List, Optional, Any, ParamSpec, TypeVar, TypeVarTuple
from atlas.boundary import Boundary, Point, Node, dataframe, geodataframe, load_boundaries
from strawberry import type, Schema, Private
from strawberry.dataloader import DataLoader
from shapely.geometry import shape
from shapely import wkb
import dabbas as db
from atlas.schema import field
from atlas.db import boundary_supabase


@type
class Pincode(Boundary):
    type: Private[str] = "pincode"


@type
class Country(Boundary):
    type: Private[str] = "country"
    name: str


@type
class State(Boundary):
    type: Private[str] = "state"

    @field
    def country(self) -> Country:
        return india

    @field
    def districts(self) -> List["District"]:
        return [muz]

    @field
    def pincodes(self) -> List["Pincode"]:
        pincodes = boundary_supabase.table('pincode').select(
            '*').eq("state_name", "Delhi").limit(10).execute().data
        return [Pincode(id='pincode:' + str(pincode['id']), pincode=pincode['pincode'], name=pincode['pincode'], _geometry=pincode['geom']) for pincode in pincodes]


@type
class District(Boundary):
    type: Private[str] = "district"

    @property
    @geodataframe
    def pincodes(self) -> List[Pincode]:
        pincodes = boundary_supabase.table('pincode').select(
            'id,pincode').eq("district_name", self.name).execute().data
        return [Pincode(_id=pincode['id'], name=pincode['pincode']) for pincode in pincodes]

    @property
    def state(self) -> "State":
        state = boundary_supabase.table('state').select(
            'id,name,district!inner(id)').eq("district.id", self._id).execute().data[0]
        return State(_id=state['id'], name=state['name'])

    @field(name="pincodes")
    async def pincodes_async(self) -> List[Pincode]:
        pincodes = boundary_supabase.table('pincode').select(
            'id,pincode').eq("districtname", self.name).execute().data
        return [Pincode(_id=pincode['id'], name=pincode['pincode']) for pincode in pincodes]

    @field(name="state")
    async def state_async(self) -> State:
        state = boundary_supabase.table('state').select(
            'id,name,district!inner(id)').eq("district.id", self._id).execute().data[0]
        return State(_id=state['id'], name=state['name'])


@type
class DataProperty(Node):
    name: str
    value: float
    node: Node
    description: Optional[str] = field(
        description='Description of the data point')


@type
class PoI(Point):
    type: Private[str] = "poi"
    name: str
    pass


class Atlas:
    def districts(country: Optional[str] = None,
                  state: Optional[str] = None) -> List[District]:
        assert state is not None, "State is required"
        return [District(_id=row['id'], name=row['name']) for row in boundary_supabase.table('district').select('id, name, state!inner(id,name)').eq(
            'state.name', state).execute().data]

    def district(name: Optional[str]) -> District:
        rows = boundary_supabase.table('district').select(
            'id,name').eq('name', name).execute().data
        if len(rows) == 0:
            raise Exception("District not found")
        district = rows[0]
        return District(_id=district['id'], name=district['name'])

    def countries() -> List[Country]:
        return [india]

    def stores(brand: str) -> List[PoI]:
        cols, results = db.query(
            "select store.id, store.name from store inner join brand on brand.name = store.l1_brand where brand.name = '{}'".format(brand))
        return [PoI(_id=row[0], name=row[1]) for row in results]

    def poi(query: str) -> List[PoI]:
        cond = ""
        # if category is not None:
        #     cond = cond + "poi.category = '{}'".format(category)
        # if subcategory is not None:
        #     cond = cond + "poi.subcategory = '{}'".format(subcategory)
        cols, results = db.query(
            "select id, name, geometry from poi {}".format(query))
        return [PoI(_id=row[0], name=row[1], _geometry=wkb.loads(row[2])) for row in results]

    def states(country: Optional[str] = None) -> List[State]:
        rows = boundary_supabase.table('state').select(
            'id', 'name').execute().data
        return [State(_id=state['id'], name=state['name']) for state in rows]

    def state(name: str) -> State:
        rows = boundary_supabase.table('state').select(
            'id', 'name').eq('name', name).execute().data
        if len(rows) == 0:
            raise Exception("State not found")
        state = rows[0]
        return State(_id=state['id'], name=state['name'])

    def pincodes(district: Optional[str] = None) -> List[Pincode]:
        pincodes = boundary_supabase.table('pincode').select(
            'id,pincode').ilike("district_name", district).execute().data
        return [Pincode(_id=pincode['id'], name=pincode['pincode']) for pincode in pincodes]

    def pincode(pincode: str) -> List[Pincode]:
        rows = boundary_supabase.table('pincode').select(
            'id,pincode').eq("pincode", pincode).execute().data

        if len(rows) == 0:
            raise Exception("Pincode not found")
        pincode = rows[0]
        return Pincode(_id=pincode['id'], name=pincode['name'])


districts = geodataframe(Atlas.districts)
district = Atlas.district
states = geodataframe(Atlas.states)
state = Atlas.state
pincodes = geodataframe(Atlas.pincodes)
countries = dataframe(Atlas.countries)
poi = geodataframe(Atlas.poi)
stores = Atlas.stores
pincode = Atlas.pincode


@type
class Query:
    @field
    def const(self, t: str) -> str:
        return t

    @field
    def query(self) -> "Query":
        return Query()

    countries = field(Atlas.countries)
    districts = field(Atlas.districts)
    district = field(Atlas.district)
    states = field(Atlas.states)
    state = field(Atlas.state)
    pincodes = field(Atlas.pincodes)
    poi = field(Atlas.poi)
    stores = field(Atlas.stores)
    pincode = field(Atlas.pincode)

    @field
    def affluence(self, location: str, segment_by: str) -> List[DataProperty]:
        return [DataProperty(id='affluence:state:1', name='affluence', value=0.5, node=bihar, description='Affluence')]


schema = Schema(query=Query)
