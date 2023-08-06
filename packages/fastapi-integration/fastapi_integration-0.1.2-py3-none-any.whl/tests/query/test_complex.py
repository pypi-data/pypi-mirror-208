import random
import string
import unittest
from statistics import mean
import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    select,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from fastapi_integration.db import SqlEngine
from fastapi_integration.models import AbstractModel

from tests.base import MyConfig


class TestQueryMixin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await db_engine.drop_database(Base)
        await db_engine.create_database(Base)

    async def asyncTearDown(self):
        async with db_engine.engine.connect() as conn:
            await conn.close()
            await db_engine.engine.dispose()

    async def condition_map_test_generator(
            self, session, expected_result, **kwargs
    ):
        result = await Model1.objects.filter(
            **kwargs
        ).execute(session)
        self.assertEqual(len(result), expected_result)

    async def test_condition_map(self):
        async with db_engine.connection_context_manager() as session:
            time = datetime.datetime.utcnow()
            for num in range(0, 10):
                await Model1.objects.create(session, name=f"Test{num}")

            await self.condition_map_test_generator(
                session, 0, created_at__second=(time.second % 59) + 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__week=time.isocalendar()[1]
            )
            await self.condition_map_test_generator(
                session, 0, created_at__week=time.isocalendar()[2]
            )

            await self.condition_map_test_generator(
                session, 10, created_at__day=time.day
            )
            await self.condition_map_test_generator(
                session, 0, created_at__day=time.day+1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__year=time.year
            )
            await self.condition_map_test_generator(
                session, 0, created_at__year=time.year - 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__month=time.month
            )
            await self.condition_map_test_generator(
                session, 0, created_at__month=(time.month % 12) + 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__day=time.day
            )
            await self.condition_map_test_generator(
                session, 0, created_at__day=(time.day % 28) + 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__hour=time.hour
            )
            await self.condition_map_test_generator(
                session, 0, created_at__hour=(time.hour % 23) + 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__minute=time.minute
            )
            await self.condition_map_test_generator(
                session, 0, created_at__minute=(time.minute % 59) + 1
            )

            current_quarter = (time.month - 1) // 3 + 1
            await self.condition_map_test_generator(
                session, 10, created_at__quarter=current_quarter
            )
            await self.condition_map_test_generator(
                session, 0, created_at__quarter=(current_quarter % 4) + 1
            )

            iso_year, _, iso_week_day = time.isocalendar()
            await self.condition_map_test_generator(
                session, 10, created_at__iso_year=iso_year
            )
            await self.condition_map_test_generator(
                session, 0, created_at__iso_year=iso_year - 1
            )

            await self.condition_map_test_generator(
                session, 10, created_at__iso_week_day=iso_week_day
            )
            await self.condition_map_test_generator(
                session, 0, created_at__iso_week_day=iso_week_day+1
            )

            await self.condition_map_test_generator(
                session, 10, name__isnull=False
            )
            await self.condition_map_test_generator(
                session, 0, name__isnull=True
            )

    async def test_distinct(self):
        async with db_engine.connection_context_manager() as session:
            for num in range(0, 10):
                await Model1.objects.create(session, name=f"Test{num%2}")

            distinct_query = await Model1.objects.filter(
                distinct_fields=["name"], order_by="name"
            ).execute(session)
            deleted = [
                await Model1.objects.delete(session, name__contains="Test"),
            ]
            self.assertEqual(len(distinct_query), 2)
            self.assertEqual(sum(deleted), 10)

    async def test_aggregations(self):
        async with db_engine.connection_context_manager() as session:
            model1 = await Model1.objects.create(session, name="Test1")
            model2 = await Model1.objects.create(session, name="Test2")
            model3 = await Model1.objects.create(session, name="Test3")

            sum_query = await Model1.objects.aggregate(
                session, field="id", agg_func="sum"
            )
            min_query = await Model1.objects.aggregate(
                session, field="id", agg_func="min"
            )
            max_query = await Model1.objects.aggregate(
                session, field="id", agg_func="max"
            )
            count_query = await Model1.objects.aggregate(
                session, field="id", agg_func="count"
            )
            avg_query = await Model1.objects.aggregate(
                session, field="id", agg_func="avg"
            )
            self.assertEqual(
                sum_query, model1.id + model2.id + model3.id
            )
            self.assertEqual(
                min_query, min(model1.id, model2.id, model3.id)
            )
            self.assertEqual(
                max_query, max(model1.id, model2.id, model3.id)
            )
            self.assertEqual(count_query, 3)
            self.assertEqual(
                avg_query, mean([model1.id, model2.id, model3.id])
            )

    async def test_bulk_methods(self):
        async with db_engine.connection_context_manager() as session:
            obj = [{"name": "name1"}, {"name": "name2"}]
            await Model2.objects.bulk_create(session, obj)
            result = await Model2.objects.filter(name="name2").execute(session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "name2")

    async def test_where_and_join_and_selects_and_m2m(self):
        async with db_engine.connection_context_manager() as session:
            random_char = ''.join(
                random.choices(string.ascii_letters + string.digits, k=9)
            )
            obj2 = await Model2.objects.create(
                session, name=f"{random_char}_part2"
            )
            obj_manager = Model1.objects
            await obj_manager.create(session, name=f"{random_char}")
            await obj_manager.add_m2m(session, [obj2, ])
            query = await Model1.objects.filter(
                limit=20,
                select_models=[Model2, ],
                where=(
                    (Model1.name + Model2.name).icontains(random_char),
                ),
                joins=[Model1.id == Model2.id],
                id__gte=0
            ).execute(session)
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
            self.assertEqual(len(results), len(query))
            self.assertGreater(len(results), 0)
            self.assertEqual(len(results[0]), len(query[0]))
            self.assertEqual(results[0][0].id, query[0][0].id)
            self.assertEqual(results[0][1].id, query[0][1].id)


if __name__ == "__main__":
    Base = declarative_base()
    association_table = Table(
        'association', Base.metadata,
        Column('model1_id', Integer, ForeignKey('model1.id')),
        Column('model2_id', Integer, ForeignKey('model2.id'))
    )

    class Model1(AbstractModel, Base):
        __tablename__ = 'model1'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(50), nullable=True)
        created_at = Column(DateTime, default=func.now())

        model2s = relationship(
            "Model2",
            secondary=association_table, back_populates="model1s"
        )
        model3s = relationship("Model3", back_populates="model1")

    class Model2(AbstractModel, Base):
        __tablename__ = 'model2'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(50), nullable=True)

        model1s = relationship(
            "Model1",
            secondary=association_table, back_populates="model2s"
        )

    class Model3(AbstractModel, Base):
        __tablename__ = 'model3'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(50), nullable=True)
        model1_id = Column(Integer, ForeignKey('model1.id'))
        model1 = relationship("Model1", back_populates="model3s")

    db_engine = SqlEngine(MyConfig())
    unittest.main()
