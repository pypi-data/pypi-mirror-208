from typing import Generator, Type, Callable, Optional, Any

from spotlight.core.pipeline.runner.stream.source.abstract import AbstractDataSource


def generator_source(
    generator: Callable[[], Generator] = None,
    *,
    name: str = "Unnamed",
    data_processor: Optional[Callable[[Any], Any]] = None
) -> Callable[[Any], Type[AbstractDataSource]]:
    """
    This is a decorator to create a streaming data source from a generator function

    Args:
        generator (Callable[[], Generator]): Generator function that produces the data source data
        name (str): Name of the plugin
        data_processor (Optional[Callable[[Any], Any]]): Optional function for transforming the generated data before
        the data source returns streams it back
    """

    def wrap(fxn):
        process_data = data_processor if data_processor else lambda x: x
        new_data_source = type(
            name,
            (AbstractDataSource,),
            {
                "initialize": lambda *args, **kwargs: fxn(),
                "teardown": lambda *args, **kwargs: None,
                "process_data": lambda self, data: process_data(data),
            },
        )
        return new_data_source

    if generator is None:
        return wrap

    return wrap(generator)
