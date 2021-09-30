import asyncio
import inspect
from typing import Any, List, Type

from factory import base


class AsyncSQLAlchemyModelFactory(base.Factory):
    """Base class for facotries."""

    session: Any

    class Meta:
        abstract = True
        exclude = ("session",)

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of a model.

        :param args: factory args.
        :param kwargs: factory keyword-args.
        :return: created model.
        """
        instance = super().create(*args, **kwargs)
        asyncio.run(cls.session.flush())
        asyncio.run(cls.session.refresh(instance))
        return instance

    @classmethod
    def create_batch(cls, size: int, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Create batch of instances.

        :param size: instances count.
        :param args: factory args.
        :param kwargs: factory keyword-args.
        :return: List of created models.
        """
        return [cls.create(*args, **kwargs) for _ in range(size)]

    @classmethod
    def _create(
        cls,
        model_class: Type["AsyncSQLAlchemyModelFactory"],
        *args: Any,
        **kwargs: Any,
    ) -> "AsyncSQLAlchemyModelFactory":
        """
        Create a model.

        This function creates model with given arguments
        and stores it in current session.

        :param model_class: class for model generation.
        :param args: args for instance creation.
        :param **kwargs: kwargs for instance.
        :raises RuntimeError: if session was not provided.
        :return: created model.
        """
        if cls.session is None:
            raise RuntimeError("No session provided.")

        async def maker_coroutine() -> AsyncSQLAlchemyModelFactory:
            """
            Corutine that creates and saves model in DB.

            :return: created instance.
            """
            for key, value in kwargs.items():  # noqa: WPS110
                # This hack is used because when we
                # want to create an instance of async model
                # we might want to await the result of a function.
                if inspect.isawaitable(value):
                    kwargs[key] = await value
            model = model_class(*args, **kwargs)
            cls.session.add(model)
            return model

        return asyncio.run(maker_coroutine())
