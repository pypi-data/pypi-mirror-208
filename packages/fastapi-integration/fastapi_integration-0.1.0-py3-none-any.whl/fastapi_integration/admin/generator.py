import inspect

from sqladmin import ModelView, BaseView


class AdminLoader:
    def __init__(self, *args, **kwargs):
        """
        Initialize the AdminLoader object.

        Args:
            *args: Variable number of modules to scan for admin views.

            **kwargs: Additional keyword arguments to pass to the
                    `Admin` constructor.
        """
        self.kwargs = kwargs
        self._admin_views = set()
        for module in args:
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                ) and (
                    issubclass(obj, ModelView) or issubclass(obj, BaseView)
                ) and (
                    obj not in (ModelView, BaseView)
                ):
                    self._admin_views.add(obj)

    @property
    def admin_views(self):
        """
        Get the set of admin views discovered by the AdminLoader.

        Returns:
            set: A set of admin views.
        """
        return self._admin_views
