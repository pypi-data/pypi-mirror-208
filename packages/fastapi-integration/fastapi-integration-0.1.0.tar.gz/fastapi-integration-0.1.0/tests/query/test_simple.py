import random
import string
import unittest


from sqlalchemy.orm import declarative_base


from tests.base import MyConfig
from fastapi_integration.db import SqlEngine
from fastapi_integration.models import AbstractBaseUser


def get_random_info():
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    domain = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = username + "@" + domain + ".com"
    icontain_email = username[:-3] + "@" + domain + ".com"
    return (username, email, icontain_email)


class TestQueryMixin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.random_info = get_random_info()
        self.random_info_two = get_random_info()
        await db_engine.create_database(Base)

    async def asyncTearDown(self):
        await db_engine.drop_database(Base)
        async with db_engine.engine.connect() as conn:
            await conn.close()
            await db_engine.engine.dispose()

    async def test_lazy_obj(self):
        obj1 = User.objects
        obj2 = User.objects
        obj1.id = "lazy"
        obj2.id = "lazy2"
        self.assertEqual(obj1.id, "lazy")
        self.assertEqual(obj2.id, "lazy2")

    async def test_filter_update_delete_all(self):
        async with db_engine.connection_context_manager() as session:
            await User.objects.create(
                email=self.random_info[1],
                username=self.random_info[0],
                password="testpassword",
                db_session=session
            )
            await User.objects.create(
                email=self.random_info_two[1],
                username=self.random_info_two[0],
                password="testpassword2",
                db_session=session
            )
            await User.objects.update(
                session,
                email=self.random_info[1],
                data={"username": "NewUser"}
            )
            res = await User.objects.get(session, username="NewUser")
            self.all_query = await User.objects.all().execute(
                db_session=session
            )
            self.delete = await User.objects.delete(
                email=self.random_info[1], db_session=session
            )

        self.assertEqual(res.username, "NewUser")
        self.assertEqual(self.delete, 1)
        self.assertGreater(len(self.all_query), 1)

    async def test_user_field_looksup(self):
        async with db_engine.connection_context_manager() as session:
            new_email = str(self.random_info[1]).join(random.choices(
                string.ascii_lowercase, k=2)
            )
            new_username = str(self.random_info[2]).join(random.choices(
                string.ascii_lowercase, k=2)
            )
            await User.objects.create(
                email=self.random_info[1], username=self.random_info[0],
                password="testpassword", db_session=session
            )
            await User.objects.create(
                email=new_email, username=new_username,
                password="testpassword", db_session=session
            )
            self.filter_gte = await User.objects.filter(
                id__gte=1
            ).execute(db_session=session, )
            self.filter_lte = await User.objects.filter(
                id__lte=0
            ).execute(db_session=session, )
            self.filter_icontain = await User.objects.filter(
                email__icontains=self.random_info[2][:2]
            ).execute(db_session=session)
            self.startswith = await User.objects.filter(
                username__startswith=self.random_info[1][:3]
            ).execute(db_session=session)
            self.istartswith = await User.objects.filter(
                username__istartswith=self.random_info[1][:3].upper(),
            ).execute(db_session=session)

        self.assertEqual(len(self.filter_icontain), 2)
        self.assertGreater(len(self.filter_gte), 0)
        self.assertEqual(len(self.filter_lte), 0)
        self.assertEqual(len(self.startswith), 1)
        self.assertEqual(len(self.istartswith), 1)

    async def test_user_exclude(self):
        async with db_engine.connection_context_manager() as session:
            await User.objects.create(
                email=self.random_info[1],
                username=self.random_info[0],
                password="testpassword",
                db_session=session
            )
            await User.objects.create(
                email=self.random_info_two[1],
                username=self.random_info_two[0],
                password="testpassword2",
                db_session=session
            )
            self.exclude_lte = await User.objects.exclude(
                id__gte=1,
                db_session=session
            )
            self.multiple_exclude_lte = await User.objects.exclude(
                id__gte=500,
                email="",
                db_session=session
            )
        self.assertGreater(len(self.multiple_exclude_lte), 0)
        self.assertEqual(len(self.exclude_lte), 0)

    async def test_query_order_limit(self):
        async with db_engine.connection_context_manager() as session:
            new_email = str(self.random_info[1]).join(
                random.choices(string.ascii_lowercase, k=2)
            )
            new_username = str(self.random_info[2]).join(
                random.choices(string.ascii_lowercase, k=2)
            )
            await User.objects.create(
                email=self.random_info[1],
                username=self.random_info[0],
                password="testpassword",
                db_session=session
            )
            await User.objects.create(
                email=new_email,
                username=new_username,
                password="testpassword",
                db_session=session
            )
            limit_query = await User.objects.filter(
                order_by="-id",
                limit=1
            ).execute(db_session=session)
            order_query = await User.objects.filter(
                order_by="-id",
                limit=2
            ).execute(db_session=session)

        self.assertEqual(len(limit_query), 1)
        self.assertGreater(order_query[0].id, order_query[1].id)

    async def test_values(self):
        async with db_engine.connection_context_manager() as session:
            await User.objects.create(
                email=self.random_info[1],
                username=self.random_info[0],
                password="testpassword",
                db_session=session
            )
            value_query = await User.objects.filter(
                email=self.random_info[1],
                values_fields=["username", "id"]
            ).execute(db_session=session)
        self.assertEqual(hasattr(value_query[0], 'password'), False)


if __name__ == "__main__":
    Base = declarative_base()

    class User(AbstractBaseUser, Base):
        __tablename__ = "users"

    db_engine = SqlEngine(MyConfig())
    unittest.main()
