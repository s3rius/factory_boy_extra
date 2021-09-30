# Extra factories for factory_boy

This library contains 2 base factories.
* AsyncSQLAlchemyModelFactory
* TortoiseModelFactory


## TortoiseModelFactory
Is made to use it with tortoise-orm.

### Usage

It works aout of the box, if you have already initialized 
tortoise-orm for testing.

You can check how to do this in [tortoise docs](https://tortoise-orm.readthedocs.io/en/latest/contrib/unittest.html#py-test).

```python
import factory
from tortoise import fields, models
from factory_boy_extra.tortoise_factory import TortoiseModelFactory


class TargetModel(models.Model):
    name = fields.CharField(max_length=200)


class TargetModelFactory(TortoiseModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = TargetModel
```

That's it. Now you can use it in your tests, E.G.

```python
@pytest.mark.asyncio
async def test_factories():
    targets = TargetModelFactory.create_batch(10)
    actual_models = await TargetModel.all()
    assert len(actual_models) == 10
```

## AsyncSQLAlchemyModelFactory

### Usage
At your conftest.py initialize your factories
with AsyncSession.

```python
@pytest.fixture(autouse=True)
def init_factories(dbsession: AsyncSession) -> None:
    """Init factories."""
    BaseFactory.session = dbsession
```

The dbsession factory can be obtained in [pytest-async-sqlalchemy](https://pypi.org/project/pytest-async-sqlalchemy/) library,
or you can add it by yourself:

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
async def dbsession():
    """
    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.
    """
    engine = create_async_engine(database_url) # You must provide your database URL.
    connection = await engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = Session()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await engine.dispose()
```

Now you can create factories and use them in your tests.

```python
from factory_boy_extra.async_sqlalchemy_factory import AsyncSQLAlchemyModelFactory

class TargetModel(Base):

    __tablename__ = "targetmodel"

    name = Column(String(length=120), nullable=False)  # noqa: WPS432


class TargetModelFactory(AsyncSQLAlchemyModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = TargetModel
```

In tests it wil look like this:
```python
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest.mark.asyncio
async def test_successful_notification(dbsession: AsyncSession) -> None:
    TargetModelFactory.create_batch(10)
    actual_models = (await dbsession.execute(select(TargetModel))).fetchall()
    assert len(actual_models) == 10
```