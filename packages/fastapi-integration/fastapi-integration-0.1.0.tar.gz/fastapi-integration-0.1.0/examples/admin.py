from examples.base import Users
from sqladmin import ModelView


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.username]
