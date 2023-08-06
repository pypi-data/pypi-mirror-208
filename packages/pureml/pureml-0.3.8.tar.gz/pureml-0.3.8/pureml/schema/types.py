from enum import Enum


class DataTypes(Enum):
    PD_DATAFRAME = "pandas dataframe"
    NUMPY_NDARRAY = "numpy ndarray"
    TEXT = "text"
    IMAGE = "image"
    JSON = "json"
