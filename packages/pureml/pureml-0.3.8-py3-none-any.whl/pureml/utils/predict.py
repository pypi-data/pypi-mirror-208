from fastapi import Request, UploadFile
from pureml.predictor.predictor import BasePredictor
from pureml.schema.predict import Input, Output
import json
from .package import parse_input, parse_output
import shutil


async def predict_request_with_json(request: Request, predictor: BasePredictor):

    # input_type, input_shape = process_input(input=predictor.input)
    # output_type, output_shape = process_output(output=predictor.output)
    print("predictor.input", predictor.input)
    print("input_type", predictor.input.type)
    print("input_shape", predictor.input.shape)
    print("output_type", predictor.output.type)
    print("output_shape", predictor.output.shape)

    headers = request.headers
    body = await request.json()
    data_json = body["test_data"]
    print("data_json", data_json)

    data = parse_input(
        data=data_json,
        input_type=predictor.input.type,
        input_shape=predictor.input.shape,
    )

    if data is None:
        print("Error in data input format")
        predictions = json.dumps(None)
        return predictions

    predictions = predictor.predict(data)
    print("predictions", predictions)

    predictions = parse_output(
        data=predictions,
        output_type=predictor.output.type,
        output_shape=predictor.output.shape,
    )

    return predictions


async def predict_request_with_file(file: UploadFile, predictor: BasePredictor):

    # input_type, input_shape = process_input(input=predictor.input)
    # output_type, output_shape = process_output(output=predictor.output)
    print("predictor.input", predictor.input)
    print("input_type", predictor.input.type)
    print("input_shape", predictor.input.shape)
    print("output_type", predictor.output.type)
    print("output_shape", predictor.output.shape)

    if predictor.input.type == "None":
        print("Rebuild the docker container with non null input_type")
        predictions = json.dumps(None)
        return predictions

    path = None

    if not file:
        print("No upload file sent")
        predictions = json.dumps(None)
        return predictions
    else:
        path = file.filename
        print(path)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    if path is None:
        print("Input image path is None")
        predictions = json.dumps(None)
        return predictions

    data = parse_input(
        data=path, input_type=predictor.input.type, input_shape=predictor.input.shape
    )

    if data is None:
        print("Error in data input format")
        predictions = json.dumps(None)
        return predictions

    predictions = predictor.predict(data)

    predictions = parse_output(
        data=predictions,
        output_type=predictor.output.type,
        output_shape=predictor.output.shape,
    )

    return predictions
