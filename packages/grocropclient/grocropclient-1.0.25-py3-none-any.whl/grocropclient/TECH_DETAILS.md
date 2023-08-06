# Tech Details about the US Crop Python Client

The motivation for the US Crop Python Client is 3-fold
1. provide a stop-gap for data not yet available via the Gro API
2. provide a stop-gap for missing permissions
3. provide a better user experience for API users

The structure of the US Crop Python Client is similar to the Climate Tier Python Client: a Python wrapper on top of the Gro Python Client API, intercepting all methods and enforcing filtering and other transformations.

Because the US Crop domain is smaller in terms of items, regions, metrics, it is doable to creatin some Python `ENUM`s to map between names and id.
* `SourceList` for sources
* `MetricList` for metrics
* `CropList` for items
* `US_States` for US states
* `US_Counties` for US counties

These lists are automatically generated using SQL queries.

They are used to enforce that items (resp. metrics, regions) requested by API users are part of the tier.

You don't have to remember ids or use the API for lookups. And they should make your code easier to write and read, e.g.
* `CropList.CORN`
* `US_Counties.ILLINOIS__ADAMS`
* `Source.DTN`

The code base is organized as follows:
- `gro_crop_client.py` is the main module API users will import in their code.
- `constants.py` contains the various ENUMs.
- `crop_budgets.py` handles crop budgets: getting the list of all budgets, retrieving one budget, pretty printing, etc.
- `crop_budgets_data.py` contains the list of all budgets. (to be deprecated and replace by API call)

The `gro_crop_client.py` is structured as follows:
- we replicate the structure of the Climate Tier Client by overriding the main methods from the Gro Client API
- we provide a suite of helper methods to deal with the various sections of the US Farmer Profitability & Crop Budgets app: yield, area, price, etc.

## Other noteworthy details

### How we handle `search`
We want to restrict the search functionality of the API to items (resp. metrics) within the tier.
We use the same approach as we did for the Climate Tier: we create a mini-corpus for items (resp. metrics) and use the `fuzzyfuzz` Python package to implement a fulltext search capability. The corpus is constructed from the names used in the items (resp. metrics) names.

### Handling ENUMs as ids
The Python ENUMs we use to map items, metrics, regions, etc. encapsulate the id which can be accessed using the `.value` attribute. To make the code cleaner, we want to use `CropList.CORN` instead of `CropList.CORN.value`. To deal with that, we have created the `handle_enums()` function that takes a dictionary (the ones with use in `get_dataseries` for instance) and transforms ENUMs into their integer value. The function handles both single values and list of values.

### Enforcing tier constraints
We are trying our best to enforce constraints when searching or accessing data. This is work in progress and we can keep adding more.
