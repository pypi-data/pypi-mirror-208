# FastAPI Integration

FastAPI Integration Package simplifies FastAPI-ORM integration with pre-built models, using SQLAlchemy and Asyncpg, saving dev time and makes it easy to load new features.


## Table Of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Goals](#goals)
- [Why do I want to create this library?](#why)
- [Why didn't I use tortoise ORM?](#tortoise-orm)
- [Contributing](#contributing)
- [License](#license)


## Installation

You can install the package using pip:
```
pip install fastapi-integration
```



## Usage

You can see a sample usage example, in exmaples folder.
For admin panel, we have laverage the use of SQLAdmin, and made integration easier.
To use the package, simply import the relevant classes and models into your FastAPI application:

```python
import logging

import uvicorn
from fastapi import APIRouter
from sqlalchemy.orm import declarative_base

from fastapi_integration.features import JwtAuthentication, UserRegistration
from fastapi_integration.models import AbstractBaseUser
from fastapi_integration import FastAPIExtended, FastApiConfig
from fastapi_integration.db import SqlEngine

base = declarative_base()

class MyConfig(FastApiConfig):
    debug: bool = True
    secret_key: str = "..."
    title: str = "..."

engine = SqlEngine(MyConfig())

class Users(AbstractBaseUser, base):
    __tablename__ = "users"


test_router = APIRouter()


@test_router.get("/")
def hello_world():
    return {"message": "Hello, world!"}


app = FastAPIExtended(
    base=base,
    db_engine=engine,
    features=[
        MyConfig,
        JwtAuthentication("/auth", Users, tags=["user"]),
        UserRegistration("/users", Users, tags=["user"])
    ],
    routers=[
        test_router
    ]
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "main:app", host="0.0.0.0", port=7979, reload=True, workers=1
    )
```


## Features

This package aims to have the following features:

1. Injectable features very easily, when initializating the fastapi main class on-demand
2. Handling dependencies of injection with DFS algorithm
3. Translated ORM written from sqlalchemy, which makes sqlalchemy to looks like django's ORM, but works with asyncpg, with still ability to use the bare SQLAlchemy if you wish to.
4. Admin support panel for backend, using Registry pattern
5. Built-in CRUD with dependencies on PostgreSQ
6. CLI for fastapi
7. Celery on-demand integration
8. Folder's Structure creation command, if needed, not sure about this yet


## Goals
- [x] Initialize project repository
- [x] Initialize project's structure and folders, with configuration
- [x] Setup Workflow
- [x] Basic CRUD integration
- [x] Implement ORM core functionality
- [x] Structure up the dependancy injections with DFS algorithm
- [x] Basic admin backend integration
- [ ] Finish basic ORM core functionality
- [ ] Extand and improve tests, also by switching to PyTests
- [ ] Finish advanced CRUD integration
- [ ] Create CLI enviroment
- [ ] Advanced admin backend integration with passing all tests 
- [ ] Integrate celery and celery beat
- [ ] First stable version!


## Features Required To Be Added
- [x] JWT Authentication
- [x] User Registration
- [x] Admin Panel
- [ ] Celery
- [ ] Celery Beat For FastAPI
- [ ] Flower


## ORM Translation's Map
**Basic** 
- [x] double underline notation
- [x] .get
- [x] .filter
- [x] .count
- [x] .exclude
- [x] .create
- [x] .update
- [x] .delete
- [x] .all
- [x] .get_or_create
- [x] .add_m2m
- [x] exact
- [x] iexact
- [x] contains
- [x] icontains
- [x] in
- [x] gt
- [x] gte
- [x] lt
- [x] lte
- [x] startswith
- [x] istartswith
- [x] endswith
- [x] iendswith
- [x] range
- [x] date
- [x] year
- [x] month
- [x] day
- [x] week
- [x] week_day
- [x] iso_week_day
- [x] iso_year
- [x] quarter
- [x] time
- [x] hour
- [x] minute
- [x] second
- [x] isnull
- [x] regex
- [x] iregex
- [ ] .contains
- [ ] .update_or_create
- [ ] .bulk_create
- [ ] .distinct
- [ ] .none
- [ ] .dates
- [ ] .datetimes
- [ ] .dates
- [ ] .dates
- [ ] .dates
- [ ] .raw
- [ ] .latest
- [ ] .earliest
- [ ] .first
- [ ] .exists
- [ ] .explain
- [ ] expressions
- [ ] output_field
- [ ] filter
- [ ] default
- [ ] **extra
- [ ] Avg
- [ ] Count
- [ ] Max
- [ ] Min
- [ ] StdDev
- [ ] Sum
- [ ] Variance

**Intermediate**
- [x] .select_related
- [x] .prefetch_related
- [x] .aggregate
- [x] .annotate
- [x] .values_list
- [x] .values
- [ ] .bulk_update
- [ ] .union
- [ ] .intersection
- [ ] .difference
- [ ] .select_for_update
- [ ] .using
- [ ] .only
- [ ] .defer
- [ ] Operations
- [ ] .in_bulk
- [ ] Prefetch

**Advanced**
- [ ] Q
- [ ] expressions
- [ ] subquery
- [ ] transaction
- [ ] custom manager methods
- [ ] custom queryset methods
- [ ] recursive CTE
- [ ] extra
- [ ] FilteredRelation
- [ ] .prefetch_related_objects


## Why

Django allows you to write acceptable code with no studding of architecture principles. It does not allow you to write good code, but it protects you from writing very bad code. In FastAPI you have ability to go both ways. With this library, as time goes by, it will protect you to not write very bad code, however you can still bypass all these protections, and write your own code if you know what you are up to.
So, if you're more of a beginner in web development and you have no good fundamental of architecture principles, then you're welcome here and let us handle that for you!


## Tortoise ORM
Although Tortoise ORM is a great option for ORM, this repository is not solely focused on providing an ORM solution. Instead, it aims to introduce beginners to SQL Alchemy and its concepts. Although the code would look different from the SQL Alchemy, the core concept of querying the database remains the same, which still uses SQL Alchemy syntax. Another thing is that Tortoise is newborn ORM, it is impossible to query the below query using Tortoise ORM.
This approach of introducing beginners to SQL Alchemy and providing the flexibility to use more advanced statements directly from SQL Alchemy is what makes this repository unique, but at same time it does not limit the developers to another new-born ORM and allows them to use SQL Alchemy alongside the translated ORM, all while following the best practices of Fast API.


```python
# SQLAlchemy Way
query2 = select(
    Model1, Model2
).select_from(
    Model1
).join(
    Model2, Model1.id == Model2.id
).where(
    (Model1.name + Model2.name).icontains(random_char) &
    (Model1.id >= 0)
).limit(
    20
)
items2 = await session.execute(query2)
results = items2.all()


# Tortoise
print("LOL!")
```



## Contributing

If you would like to contribute to this package, please feel free to submit a pull request or create an issue on the GitHub repository.

## License

This package is licensed under the MIT License.