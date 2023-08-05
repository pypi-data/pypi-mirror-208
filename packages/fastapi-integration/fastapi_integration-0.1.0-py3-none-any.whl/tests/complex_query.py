import resolve_path
import random
import string
import unittest
import time
from statistics import mean

from sqlalchemy import Column, Integer, String, ForeignKey, Table, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from fastapi_integration.db import Engine
from fastapi_integration.models import AbstractModel

from tests.start import MyConfig


class TestQueryMixin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await db_engine.drop_database(Base)
        await db_engine.create_database(Base)

    async def asyncTearDown(self):
        async with db_engine.engine.connect() as conn:
            await conn.close()
            await db_engine.engine.dispose()

    async def test_double_underline_notation_and_perfomance(self):
        async def test_case1():
            async with db_engine.get_pg_db_with_async() as session:
                model1 = Model1(name=random_chars)
                session.add(model1)
                model3 = Model3(model1=model1)
                session.add(model3)
                await session.flush()

                stmt = select(Model3).join(Model1).filter(
                    Model1.name == random_chars
                ).limit(20)
                result = await session.execute(stmt)
                query = result.scalars().all()

                await session.commit()
                await session.delete(model3)
                await session.delete(model1)
                await session.commit()

            return query

        async def test_case2(test_contains=False):
            async with db_engine.get_pg_db_with_async() as session:
                model1 = await Model1.objects.create(
                    session, name=random_chars
                )
                await Model3.objects.create(session, model1=model1)
                query = await Model3.objects.filter(
                    session, model1__name=random_chars
                )

                if test_contains:
                    query2 = await Model3.objects.filter(
                        session, model1__name__contains=random_chars[:5]
                    )
                    query3 = await Model3.objects.filter(
                        session,
                        model1__name__icontains=random_chars[:5].upper()
                    )
                else:
                    query2 = None
                    query3 = None

                await Model3.objects.delete(session, model1__id=model1.id)
                await Model1.objects.delete(session, name=random_chars)

            return query, query2, query3

        num_runs = 1
        # For larger numbers, SQLAlchemy is caching and having low response
        # times better than mine.
        elapsed_times1 = []
        elapsed_times2 = []

        for _ in range(num_runs):
            random_chars = ''.join(random.choices(
                string.ascii_letters + string.digits, k=9
            ))

            start_time = time.perf_counter()
            await test_case1()
            elapsed_time1 = time.perf_counter() - start_time
            elapsed_times1.append(elapsed_time1)

            start_time = time.perf_counter()
            await test_case2()
            elapsed_time2 = time.perf_counter() - start_time
            elapsed_times2.append(elapsed_time2)

        avg_elapsed_time1 = mean(elapsed_times1)
        avg_elapsed_time2 = mean(elapsed_times2)

        random_chars = ''.join(
            random.choices(string.ascii_letters + string.digits, k=9)
        )
        query, query2, query3 = await test_case2(test_contains=True)

        self.assertEqual(len(query), 1)
        self.assertEqual(query[0].id, query2[0].id)
        self.assertEqual(query2[0].id, query3[0].id)
        self.assertGreater(avg_elapsed_time1, avg_elapsed_time2)

    async def test_distinct(self):
        async with db_engine.get_pg_db_with_async() as session:
            model1 = await Model4.objects.create(session, name="Test5")
            model2 = await Model4.objects.create(session, name="Test6")
            model3 = await Model4.objects.create(session, name="Test5")

            distinct_query = await Model4.objects.filter(
                session, distinct_fields=["name"], order_by="name"
            )
            self.assertEqual(len(distinct_query), 2)

            await Model4.objects.delete(session, id=model1.id)
            await Model4.objects.delete(session, id=model2.id)
            await Model4.objects.delete(session, id=model3.id)

    async def test_aggregations(self):
        async with db_engine.get_pg_db_with_async() as session:
            model1 = await Model1.objects.create(session, name="Test1")
            model2 = await Model1.objects.create(session, name="Test2")
            model3 = await Model1.objects.create(session, name="Test3")

            sum_query = await Model1.objects.aggregate(
                session, field="id", agg_func="sum"
            )
            self.assertEqual(
                sum_query, model1.id + model2.id + model3.id
            )

            min_query = await Model1.objects.aggregate(
                session, field="id", agg_func="min"
            )
            self.assertEqual(
                min_query, min(model1.id, model2.id, model3.id)
            )

            max_query = await Model1.objects.aggregate(
                session, field="id", agg_func="max"
            )
            self.assertEqual(
                max_query, max(model1.id, model2.id, model3.id)
            )

            count_query = await Model1.objects.aggregate(
                session, field="id", agg_func="count"
            )
            self.assertEqual(count_query, 3)

            avg_query = await Model1.objects.aggregate(
                session, field="id", agg_func="avg"
            )
            self.assertEqual(
                avg_query, mean([model1.id, model2.id, model3.id])
            )

            await Model1.objects.delete(session, id=model1.id)
            await Model1.objects.delete(session, id=model2.id)
            await Model1.objects.delete(session, id=model3.id)

    async def test_bulk_methods(self):
        async with db_engine.get_pg_db_with_async() as session:
            obj = [{"name": "name1"}, {"name": "name2"}]
            await Model2.objects.bulk_create(session, obj)
            result = await Model2.objects.filter(session, name="name2")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "name2")

            # update_data = [
            #     ({"name": "name1"}, {"name": "name3"}),
            #     ({"name": "name2"}, {"name": "name4"}),
            # ]
            # await Model2.objects.bulk_update(session, update_data)
            # result1 = await Model2.objects.filter(session, name="name3")
            # result2 = await Model2.objects.filter(session, name="name4")
            # self.assertEqual(len(result1)+len(result2), 2)
            # self.assertEqual(result1[0].name, "name3")
            # self.assertEqual(result1[0].name, "name4")

    async def test_where_and_join_and_selects_and_m2m(self):
        async with db_engine.get_pg_db_with_async() as session:
            random_char = ''.join(
                random.choices(string.ascii_letters + string.digits, k=9)
            )
            model2 = await Model2.objects.create(
                session, name=f"{random_char}_part2"
            )
            obj_manager = Model1.objects
            await obj_manager.create(session, name=f"{random_char}")
            await obj_manager.add_m2m(session, model2)
            # result2 = await Model1.objects.all(session)
            # result = await Model1.objects.prefetch_related(Model2).all(
            #   session
            # )

            # My way
            query = await Model1.objects.filter(
                session,
                limit=20,
                select_models=[Model2, ],
                where=(
                    (Model1.name + Model2.name).icontains(random_char),
                ),
                joins=[Model1.id == Model2.id],
                id__gte=0
            )

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
            self.assertEqual(len(results), len(query))
            assert len(results) > 0, """
                Query did not found the correspanding models,
                please check the DB.
            """
            self.assertEqual(len(results[0]), len(query[0]))
            self.assertEqual(results[0][0].id, query[0][0].id)
            self.assertEqual(results[0][1].id, query[0][1].id)


if __name__ == "__main__":
    resolve_path
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

    class Model4(AbstractModel, Base):
        __tablename__ = 'model4'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(50), nullable=True)

    db_engine = Engine(MyConfig())
    unittest.main()
