import os
import joblib
from collections import defaultdict, OrderedDict
from pureml.schema import PathSchema, ConfigKeys


path_schema = PathSchema().get_instance()
config_keys = ConfigKeys


def load_config():
    os.makedirs(path_schema.PATH_USER_PROJECT_DIR, exist_ok=True)

    if os.path.exists(path_schema.PATH_CONFIG):
        config = joblib.load(path_schema.PATH_CONFIG)
    else:
        config = defaultdict()

        config[config_keys.load_data.value] = defaultdict()
        config[config_keys.transformer.value] = OrderedDict()
        config[config_keys.dataset.value] = defaultdict()

        config[config_keys.model.value] = OrderedDict()

        config[config_keys.params.value] = defaultdict()
        config[config_keys.metrics.value] = defaultdict()
        config[config_keys.figure.value] = defaultdict()
        config[config_keys.artifacts.value] = defaultdict()

        config[config_keys.pred_function.value] = defaultdict()
        config[config_keys.pip_requirement.value] = defaultdict()
        config[config_keys.resource.value] = defaultdict()

        joblib.dump(config, path_schema.PATH_CONFIG)

    return config


def save_config(config):
    save_dir = os.path.dirname(path_schema.PATH_CONFIG)

    os.makedirs(save_dir, exist_ok=True)
    # print('config')
    # print(config)

    joblib.dump(config, path_schema.PATH_CONFIG)


def reset_config(key):
    if os.path.exists(path_schema.PATH_CONFIG):
        config = joblib.load(path_schema.PATH_CONFIG)
        if key in config.keys():
            if key in [config_keys.transformer.value, config_keys.model.value]:
                config[key] = OrderedDict()
            else:
                config[key] = defaultdict()
            save_config(config)
