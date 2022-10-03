import asyncio
from cProfile import run
from typing import Any

import nest_asyncio
from factory import base


class TortoiseModelFactory(base.Factory):
    """Base factory for tortoise factory."""

    class Meta:
        abstract = True

    @classmethod
    def _create(
        cls,
        model_class,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Creates an instance of Tortoise model.

        :param model_class: model class.
        :param args: factory args.
        :param kwargs: factory keyword-args.
        :return: instance of model class.
        """
        instance = model_class(*args, **kwargs)

        async def save_instance(model_instance):
            await model_instance.save()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop:
            # patch asyncio to allow nesting loops.
            # https://github.com/erdewit/nest_asyncio
            nest_asyncio.apply(loop=loop)

            # because of the patch a database connections lingers after the factory
            # is done and that prevents the database from closing after the tests.
            # unless Tortoise.connection.connections.close_all() is called from within the test,
            # the test teardown always fails, even with conftest teardown
            # RuntimeError: Task is attached to a different loop

            asyncio.get_event_loop().run_until_complete(
                save_instance(instance)
            )

        else:
            asyncio.run(save_instance(instance))

        return instance
