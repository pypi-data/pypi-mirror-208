import pandas as pd
import numpy as np
from PIL import Image
import json
from pureml.schema import DataTypes


def process_input(input):

    input_type = ""
    input_shape = None

    if input is not None:
        input_keys = input.keys()

        if "type" in input_keys:
            input_type = input["type"]
        if "shape" in input_keys:
            input_shape = input["shape"]

    return input_type, input_shape


def process_output(output):

    output_type = ""
    output_shape = None

    if output is not None:
        output_keys = output.keys()

        if "type" in output_keys:
            output_type = output["type"]
        if "shape" in output_keys:
            output_shape = output["shape"]

    return output_type, output_shape


def parse_input(data, input_type, input_shape):
    # if input_type == 'json':
    #     data = data

    if input_type == DataTypes.NUMPY_NDARRAY:
        if type(data) == str:
            data = json.loads(data)
        data = np.array(data)
        data = data.reshape(input_shape)
    elif input_type == DataTypes.PD_DATAFRAME:
        if type(data) == str:
            data = json.loads(data)
        data = pd.DataFrame.from_dict(data)
    elif input_type == DataTypes.TEXT:
        data = json.loads(data)
    elif input_type == DataTypes.IMAGE:
        data = Image.open(data)
        data = np.array(data)
        print("input image shape", data.shape)
    else:
        data = None

    print("input data type", type(data))
    # print(data)

    return data


def parse_output(data, output_type, output_shape):
    # if input_type == 'json':
    #     data = data

    if output_type == DataTypes.NUMPY_NDARRAY:
        data = data.tolist()
        data = json.dumps(data)
    elif output_type == DataTypes.PD_DATAFRAME:
        data = data.to_dict()
        data = json.dumps(data)
    elif output_type == DataTypes.TEXT:
        data = json.dumps(data)
    else:
        data = json.dumps(data)

    return data
