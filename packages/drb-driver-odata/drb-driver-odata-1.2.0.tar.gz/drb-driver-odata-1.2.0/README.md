# OData driver
This drb-driver-odata module implements the OData protocol access
following the Copernicus Space Component schema with DRB
data model. It is able to navigate among Product entities of a OData
service.

# Nodes
### ODataServiceNode
Represents the OData service. There are 3 type of service `ODataServiceNodeCSC`, `ODataServiceNodeDhus` and `ODataServiceNodeDias`. These nodes has no attribute and
has as children Product entities of the service defined by
`ProductNode`.
A specific `ProductNode` can be retrieved during the bracket and
slash navigation by his *Name*(str) or by his *Id*(UUID).

OData services required can be access using the second (optional)
parameter __auth__ of _ODataServiceNode_, this parameter must be an
_requests.auth.AuthBase_ object, see
[requests documentation](https://docs.python-requests.org/en/latest/user/authentication)
for more details.
### ODataProductNode
Represents a *Product* entity of the OData service. This
node has as attribute properties of the associated entity and has
for unique child a `ProductAttributeNode`
### ODataProductAttributeNode
This node allowing to represent the navigation link between the
*Product* entity and its attributes. It has no attribute and has as
children *Attribute* entities associated to the *Product* entity,
defined by `AttributeNode`
### ODataAttributeNode
Represents an *Attribute* entity. This node has no child and has as
attribute properties associated to the *Attribute* entity.

# Predicate
### ODataCustomQuery
This predicate allows to retrieve a specific subset of children of an
_ODataServiceNode_.


# Cache set up

Some cache has been implemented to limit the number of requests to the server. 
These cache evicts cache entries based on both time and space.
the time and the cache size can be changed by adding these two variables to the runtime environment.
```python
DRB_ODATA_NODE_REQUEST_CACHE_EXPIRE_TIME_SEC = 120
DRB_ODATA_NODE_REQUEST_CACHE_MAX_ELEMENTS = 32
```

Here are all the queries that use a cache
```
def req_svc(odata: OdataNode) -> dict:
def req_svc_products(odata: OdataNode, **kwargs) -> list:
def req_product_by_uuid(odata: OdataNode, prd_uuid: str) -> dict:
def req_product_attributes(odata: OdataNode, prd_uuid: str) -> List[dict]:
```

The time of the cache eviction can be change by calling `reset_cache_expiration_time(sec=1) `: 
```
req_svc_products.reset_expiration_time(sec=1)
```

# Installation
```
pip install drb-driver-odata
```
# Examples

```python
from uuid import UUID
from drb.drivers.odata import ODataQueryPredicate, ExpressionFunc, ExpressionType
from drb.topics import resolver


# Add '+odata' for recognize the odata driver usage.
url = 'https+odata://my.csc.odata.com'

# generate ODataServiceNode corresponding to the service.
odata = resolver.create(url)

# total number of children
product_count = len(odata)

# retrieve first ODataProductNode
node_idx = odata[0]

# retrieve last ODataProductNode
node_idx = odata[-1]

# retrieve 10 first products
products = odata[:10]

# retrieve Product by name
name = 'S2B_OPER_MSI_L0__GR_EPAE_..._D05_N02.06.tar'
node_name_list = odata[name]  # returns a list
node_name = odata[name]  # returns first occurrence of the list

# retrieve Product by UUID
uuid = UUID('0723d9bf-02a2-3e99-b1b3-f6d81de84b62')
node_uuid = odata[uuid]


# get product attributes
prd_node = odata[uuid]
attr_node = prd_node['Attributes']['Footprint']

attr_type = attr_node @ 'ValueType'
attr_value = attr_node.value

# filter and order products
filtered_children = odata[
    ODataQueryPredicate(
        filter="startswith(Name,'S1')",
        order="ContentLength desc"
    )
]

# You can also use the Expression given with this driver
filtered_children = odata[
    ODataQueryPredicate(
        filter=ExpressionFunc.startswith(
        ExpressionType.property('Name'),'S1'),
        order=(ExpressionType.property('ContentLength'),
               ExpressionType.property('desc')
        )
    )
]
```

The same example with DHus catalog (https://scihub.copernicus.eu/dhus/odata/v2)

The only change is

```python

# get product attributes
# For DhuS ValueType not exist in Attributes...
attr_type = attr_node @ 'ContentType'

```

A similar example with ONDA-DIAS catalog (https://catalogue.onda-dias.eu/dias-catalogue)

```python
import uuid
from drb.drivers.odata import ODataQueryPredicate
from drb.topics import resolver

url = 'https+odata://catalogue.onda-dias.eu/dias-catalogue'

# generate ODataServiceNode corresponding to the service.
odata = resolver.create(url)

# retrieve Product by UUID
uuid_node = uuid.UUID('34a0a4ed-0246-4a57-827d-70350b96d03d')
node_uuid = odata[uuid_node]

attr_node = node_uuid['Attributes']
children = attr_node.children
foot_print = node_uuid.get_attribute('footprint')
print(foot_print)
print(attr_node['Online quality check'].value)

# search by product type limited two the 2 first result
filtered_children = odata[
    ODataQueryPredicate(
        search='"(platformName:Sentinel-2) AND (productType:S2MSI2A)"',
        top="2"
    )
]
```

# Odata Query Expression

To help the user can create query by using `ExpressionType`, `ExpressionOperator` and `ExpressionFunc`

## ExpressionType

| Function   |              Description               |                                         Example |                                      query |
|------------|:--------------------------------------:|------------------------------------------------:|-------------------------------------------:|
| bool       |   To put a boolean value in a query    |                       ExpressionType.bool(True) |                                       true |
| string     |    To put a string value in a query    |                   ExpressionType.string('toto') |                                     'toto' |
| number     | To put a int or float value in a query |                      ExpressionType.number(100) |                                        101 |
| collection |  To put an array of values in a query  |              ExpressionType.collection([1,2,3]) |                                [1,2,3,4,5] |
| property   |  To put an odata property in a query   |                 ExpressionType.property('Name') |                                       Name |
| footprint  |  To put an odata footprint in a query  | ExpressionType.footprint([(-12, 34), (32, 34))] | geography'SRID=4326;Polygon((-12 34,32 34) |

## ComparisonOperator

| Function |    Description     |                                                                                                                                  Example |                                 Query |
|----------|:------------------:|-----------------------------------------------------------------------------------------------------------------------------------------:|--------------------------------------:|
| eq       |       equal        |                                                  ComparisonOperator.eq(ExpressionType.property('My_Prop'),ExpressionType.string('Toto')) |                     My_Prop eq 'Toto' |
| ne       |     Not equal      |                                                     ComparisonOperator.ne(ExpressionType.property('My_Prop'),ExpressionType.number(100)) |                        My_Prop ne 100 |
| has      |     Has flags      |                                  ComparisonOperator.has(ExpressionType.property('Style'),ExpressionType.property("Sales.Color'Yellow'")) |         Style has Sales.Color'Yellow' |
| co_in    |   Is a member of   | ComparisonOperator.co_in(ExpressionType.property('Address/City'),GroupingOperator.group(ExpressionType.property("'Redmond', 'London'"))) | Address/City in ('Redmond', 'London') |
| lt       |     Less than      |                                                         ComparisonOperator.lt(ExpressionType.property('Price'),ExpressionType.number(20) |                           Price lt 20 |
| le       | less than or equal |                                                         ComparisonOperator.le(ExpressionType.property('Price'),ExpressionType.number(20) |                           Price le 20 |
| gt       |    greater than    |                                                         ComparisonOperator.gt(ExpressionType.property('Price'),ExpressionType.number(20) |                           Price gt 20 |
| ge       |  greater or equal  |                                                         ComparisonOperator.ge(ExpressionType.property('Price'),ExpressionType.number(20) |                           Price ge 20 |

## LogicalOperator

| Function |   Description    |                        Example |                       Query |
|----------|:----------------:|-------------------------------:|----------------------------:|
| lo_and   |   	Logical and   | LogicalOperator.lo_and(ge, gt) | Price ge 20 and Price gt 20 |
| lo_or    |   	Logical or    |  LogicalOperator.lo_or(ge, gt) |  Price ge 20 or Price gt 20 |
| lo_not   | Logical negation |     LogicalOperator.lo_not(ge) |             not Price ge 20 |


## ArithmeticOperator

| Function |   Description    |                                                                             Example |          Query |
|----------|:----------------:|------------------------------------------------------------------------------------:|---------------:|
| add      |     Addition     |   ArithmeticOperator.add(ExpressionType.property('Price'),ExpressionType.number(5)) |   Price add 20 |
| sub      |   Subtraction    |   ArithmeticOperator.sub(ExpressionType.property('Price'),ExpressionType.number(5)) |   Price sub 20 |
| mul      |  Multiplication  |   ArithmeticOperator.mul(ExpressionType.property('Price'),ExpressionType.number(5)) |   Price mul 20 |
| div      |     Division     |   ArithmeticOperator.div(ExpressionType.property('Price'),ExpressionType.number(5)) |   Price div 20 |
| divby    | Decimal Division | ArithmeticOperator.divby(ExpressionType.property('Price'),ExpressionType.number(5)) | Price divby 20 |
| mod      |      Modulo      |   ArithmeticOperator.mod(ExpressionType.property('Price'),ExpressionType.number(5)) |   Price mod 20 |


## GroupingOperator

| Function |     Description     |                                                                                                   Example |         Query |
|----------|:-------------------:|----------------------------------------------------------------------------------------------------------:|--------------:|
| group    | Precedence grouping | GroupingOperator.group(ExpressionOperator.add(ExpressionType.property('Price'),ExpressionType.number(5))) | (Price add 5) |


## ExpressionFunc

| function           |                                                                                                         Example                                                                                                         |                                            Query |
|--------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|-------------------------------------------------:|
| concat             |                                                                   ExpressionFunc.concat(ExpressionType.property('City'),ExpressionType.string(', '))                                                                    |                                concat(City,', ') |
| contains           |                                                                            ExpressionFunc.contains(ExpressionType.property('City'),'London')                                                                            |                          contains(City,'London') |
| endswith           |                                                                              ExpressionFunc.endswith(ExpressionType.property('City'),'on')                                                                              |                              endswith(City,'on') |
| startswith         |                                                                             ExpressionFunc.startswith(ExpressionType.property('City'),'Lo')                                                                             |                            startswith(City,'Lo') |
| indexof            |                                                                            ExpressionFunc.indexof(ExpressionType.property('Company'),'Gael')                                                                            |                          indexof(Company,'Gael') |
| length             |                                                                                ExpressionFunc.length(ExpressionType.property('Company'))                                                                                |                                  length(Company) |
| substring          |                                                                             ExpressionFunc.substring(ExpressionType.property('Company'),1)                                                                              |                             substring(Company,1) |
| hassubset          |                                                              ExpressionFunc.hassubset(ExpressionType.array([1, 2, 3, 4, 5]), ExpressionType.array([3, 4]))                                                              |                     hassubset([1,2,3,4,5],[3,4]) |
| hassubsequence     |                                                           ExpressionFunc.hassubsequence(ExpressionType.array([1, 2, 3, 4, 5]), ExpressionType.array([3, 5]) )                                                           |                hassubsequence([1,2,3,4,5],[3,5]) |
| matchesPattern     |                                                         ExpressionFunc.matchesPattern(ExpressionType.property('CompanyName'),ExpressionType.string('%5EA.*e$'))                                                         |           matchesPattern(CompanyName,'%5EA.*e$') |
| tolower            |                                                                             ExpressionFunc.tolower(ExpressionType.property('CompanyName'))                                                                              |                             tolower(CompanyName) |
| toupper            |                                                                             ExpressionFunc.toupper(ExpressionType.property('CompanyName'))                                                                              |                             toupper(CompanyName) |
| trim               |                                                                               ExpressionFunc.trim(ExpressionType.property('CompanyName'))                                                                               |                                trim(CompanyName) |
| day                |                                                                                ExpressionFunc.day(ExpressionType.property('StartTime'))                                                                                 |                                   day(StartTime) |
| date               |                                                                                ExpressionFunc.date(ExpressionType.property('StartTime'))                                                                                |                                  date(StartTime) |
| second             |                                                                               ExpressionFunc.second(ExpressionType.property('StartTime'))                                                                               |                                second(StartTime) |
| hour               |                                                                                ExpressionFunc.hour(ExpressionType.property('StartTime'))                                                                                |                                  hour(StartTime) |
| minute             |                                                                               ExpressionFunc.minute(ExpressionType.property('StartTime'))                                                                               |                                minute(StartTime) |
| month              |                                                                               ExpressionFunc.month(ExpressionType.property('StartTime'))                                                                                |                                 month(StartTime) |
| time               |                                                                                ExpressionFunc.time(ExpressionType.property('StartTime'))                                                                                |                                  time(StartTime) |
| totaloffsetminutes |                                                                         ExpressionFunc.totaloffsetminutes(ExpressionType.property('StartTime'))                                                                         |                    totaloffsetminutes(StartTime) |
| totalseconds       |                                                                            ExpressionFunc.totalseconds(ExpressionType.property('StartTime'))                                                                            |                          totalseconds(StartTime) |
| year               |                                                                                ExpressionFunc.year(ExpressionType.property('StartTime'))                                                                                |                                  year(StartTime) |
| maxdatetime        |                                                                            ExpressionFunc.maxdatetime(ExpressionType.property('StartTime'))                                                                             |                           maxdatetime(StartTime) |
| mindatetime        |                                                                            ExpressionFunc.mindatetime(ExpressionType.property('StartTime'))                                                                             |                           mindatetime(StartTime) |
| now                |                                                                                                  ExpressionFunc.now()                                                                                                   |                                            now() |
| ceiling            |                                                                               ExpressionFunc.ceiling(ExpressionType.property('Freight'))                                                                                |                                 ceiling(Freight) |
| floor              |                                                                                ExpressionFunc.floor(ExpressionType.property('Freight'))                                                                                 |                                   floor(Freight) |
| round              |                                                                                ExpressionFunc.round(ExpressionType.property('Freight'))                                                                                 |                                   round(Freight) |
| cast               |                                                            ExpressionFunc.cast(ExpressionType.property('ShipCountry'),ExpressionType.property('Edm.String'))                                                            |                     cast(ShipCountry,Edm.String) |
| isof               |                                                            ExpressionFunc.isof(ExpressionType.property('ShipCountry'),ExpressionType.property('Edm.String'))                                                            |                     isof(ShipCountry,Edm.String) |
| geo_distance       |                                                      ExpressionFunc.geo_distance(ExpressionType.property('CurrentPosition'),ExpressionType.property('TargetArea'))                                                      |         geo.distance(CurrentPosition,TargetArea) |
| geo_intersects     |                                                     ExpressionFunc.geo_intersects(ExpressionType.property('CurrentPosition'),ExpressionType.property('TargetArea'))                                                     |       geo.intersects(CurrentPosition,TargetArea) |
| csc_intersect      |                                                     ExpressionFunc.csc_intersect(ExpressionType.property('CurrentPosition'),ExpressionType.property('TargetArea'))                                                      | OData.CSC.Intersects(CurrentPosition,TargetArea) |
| geo_length         |                                                                            ExpressionFunc.geo_length(ExpressionType.property('DirectRoute'))                                                                            |                          geo.length(DirectRoute) |
| case               | ExpressionFunc.case([(ExpressionOperator.gt(ExpressionType.property('X'),ExpressionType.number(0)),1),(ExpressionOperator.lt(ExpressionType.property('X'),ExpressionType.number(0)),-1),(ExpressionType.bool(True),0)]) |                  case(X gt 0:1,X lt 0:-1,true:0) |
| any                |                                                    ExpressionFunc.any('a',ExpressionOperator.gt(ExpressionType.property('a/TotalPrice'),ExpressionType.number(100)))                                                    |                       any(a:a/TotalPrice gt 100) |
| all                |                                                    ExpressionFunc.all('d' ExpressionOperator.gt(ExpressionType.property('d/TotalPrice'),ExpressionType.number(100)))                                                    |                       all(d:d/TotalPrice gt 100) |

## Geographic query argument

For geographic query this driver supports:
- String query like: 
```python 
    "geography'SRID=4326;Polygon((0.0 0.0,1.0 0.0,1.0 1.0,0.0 1.0,0.0 0.0))'"
```
- List of tuple representing coordinate:
```python 
    [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
```
 
- A polygon:
```python 
    Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
```
