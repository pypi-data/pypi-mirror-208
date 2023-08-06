class SQL:
    """
    Represents the SQL dependency.

    This is a base class for SQL-related dependencies.
    """


class NoSQL:
    """
    Represents the NoSQL dependency.

    This is a base class for NoSQL-related dependencies.
    """


class SQLAlchemy(SQL):
    """
    Represents the SQLAlchemy dependency.

    This class extends the SQL dependency and represents the SQLAlchemy ORM.
    """


class PostgreSQL(SQL):
    """
    Represents the PostgreSQL dependency.

    This class extends the SQL dependency and represents the PostgreSQL.
    """


class Redis(NoSQL):
    """
    Represents the Redis dependency.

    This class extends the NoSQL dependency and represents the Redis.
    """


class UserTable(SQL):
    """
    Represents the UserTable dependency.

    This class extends the SQL dependency and represents the user table.
    """
