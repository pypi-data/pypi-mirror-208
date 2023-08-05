from typing import Callable
from typing import Optional

from datasets import Dataset


def create_from_generator(
    hub,
    generator: Callable,
    gen_kwargs: Optional[dict] = None,
):
    """
    Create a new dataset from a custom generator
    """
    return Dataset.from_generator(generator, gen_kwargs=gen_kwargs)


def pre_process(
    hub,
    dataset: Dataset,
    pre_process_func: Callable,
    pre_process_func_kwargs: Optional[dict] = None,
    format_type: str = "torch",
    columns: list = [],
):
    """
    Pre-process dataset such as tokenization, augmentation or re-sampling using custom processor
    """
    dataset = dataset.map(
        function=pre_process_func, fn_kwargs=pre_process_func_kwargs, batched=True
    )
    dataset.set_format(type=format_type, columns=columns)
    return dataset
