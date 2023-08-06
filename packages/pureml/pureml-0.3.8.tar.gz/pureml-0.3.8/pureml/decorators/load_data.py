from pureml.utils.pipeline import add_load_data_to_config
import functools


def load_data():
    def decorator(func):
        # print('Inside decorator')
        # print("decorating", func, "with argument", name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # print("Inside wrapper")
            func_name = func.__name__
            func_description = func.__doc__

            # print("func_name", func_name)
            # print("func_description", func_description)

            func_output = func(*args, **kwargs)

            add_load_data_to_config(
                name=func_name, description=func_description, func=func
            )

            res_text = ""

            return func_output

        # print("Outside  wrapper")

        return wrapper

    # print('Outside decorator')

    return decorator
