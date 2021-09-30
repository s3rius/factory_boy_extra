import asyncio
from typing import Any

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
        asyncio.run(instance.save())
        return instance
