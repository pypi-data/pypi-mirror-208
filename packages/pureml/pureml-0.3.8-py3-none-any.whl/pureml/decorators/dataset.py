from pureml.components.dataset import register
from pureml.utils.pipeline import add_dataset_to_config
from pureml.lineage.data.create_lineage import create_lineage
from pureml.utils.version_utils import parse_version_label
import functools
from pureml.utils.config import reset_config
from pureml.schema import ConfigKeys

config_keys = ConfigKeys


def dataset(label: str, parent: str = None, upload=False):
    def decorator(func):
        name, branch, _ = parse_version_label(label)

        # Add dataset name to config here if it is being used by any of the pipeline components.
        # add_dataset_to_config(name=name, parent=parent)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            func_description = func.__doc__

            func_output = func(*args, **kwargs)

            is_empty = False

            if not upload or func_output is None:
                is_empty = True

            add_dataset_to_config(
                name=name,
                branch=branch,
                description=func_description,
                parent=parent,
                func=func,
            )

            lineage = create_lineage()

            dataset_exists_in_remote, dataset_hash, dataset_version = register(
                dataset=func_output,
                label=label,
                lineage=lineage,
                is_empty=is_empty,
            )

            # Uncomment this if there any components that depend on dataset version, or dataset hash
            # if dataset_exists_in_remote:
            #     add_dataset_to_config(name=name, branch=branch, hash=dataset_hash, version=dataset_version, parent=parent, func=func)
            add_dataset_to_config(
                name=name,
                branch=branch,
                description=func_description,
                hash=dataset_hash,
                parent=parent,
                func=func,
            )

            reset_config(key=config_keys.load_data.value)
            reset_config(key=config_keys.transformer.value)
            reset_config(key=config_keys.dataset.value)

            return func_output

        return wrapper

    return decorator
