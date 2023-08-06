import os
import shutil
import uvicorn
from fastapi import FastAPI
from pureml.schema import FastAPISchema, PredictSchema, PathSchema
from pureml.utils.package import process_input, process_output
from pureml.utils.version_utils import parse_version_label
from pureml import predict, pip_requirement, resources
from pureml.utils.resources import zip_content, unzip_content
import sys


prediction_schema = PredictSchema()
fastapi_schema = FastAPISchema()
path_schema = PathSchema()


def get_resources(label, resources_path):
    resources.fetch(label=label)

    if not os.path.exists(prediction_schema.PATH_RESOURCES):

        if resources_path is None:

            resources_path = prediction_schema.PATH_RESOURCES_DIR_DEFAULT
            print("Taking the default resources path: ", resources_path)
        else:
            print("Taking the resources path: ", resources_path)

        zip_content(resources_path, prediction_schema.PATH_RESOURCES)

        if os.path.exists(prediction_schema.PATH_RESOURCES):
            unzip_content(
                prediction_schema.PATH_RESOURCES, path_schema.PATH_PREDICT_DIR
            )
        else:
            raise Exception(resources_path, "does not exists!!!")
    else:
        print("Taking the fetched resources file path")


def get_predict_file(label, predict_path):

    predict.fetch(label)

    if not os.path.exists(prediction_schema.PATH_PREDICT):
        print("[orange] Prediction Function is not logged")

        # os.makedirs(PATH_PREDICT_DIR, exist_ok=True)

        if predict_path is None:
            predict_path = prediction_schema.PATH_PREDICT_USER
            print("Taking the default predict.py file path: ", predict_path)
        else:
            print("Taking the predict.py file path: ", predict_path)

        if os.path.exists(predict_path):
            shutil.copy(predict_path, prediction_schema.PATH_PREDICT)
        else:
            raise Exception(predict_path, "does not exists!!!")
    else:
        print("Taking the fetched predict.py file path")


def get_requirements_file(label, requirements_path):
    pip_requirement.fetch(label=label)

    if not os.path.exists(prediction_schema.PATH_PREDICT_REQUIREMENTS):

        if requirements_path is None:
            requirements_path = prediction_schema.PATH_PREDICT_REQUIREMENTS_USER
            print("Taking the default requirements.txt file path: ", requirements_path)
        else:
            print("Taking the requirements.txt file path: ", requirements_path)

        if os.path.exists(requirements_path):
            shutil.copy(requirements_path, prediction_schema.PATH_PREDICT_REQUIREMENTS)
        else:
            raise Exception(requirements_path, "does not exists!!!")
    else:
        print("Taking the fetched requirements.txt file path")


def generate_api(label: str):
    name, branch, version = parse_version_label(label=label)

    api = """
from fastapi import FastAPI, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pureml
from predict import Predictor
import os
from dotenv import load_dotenv
import json
import shutil
from pureml.utils.package import process_input, process_output
from typing import Union, Optional
from pureml.utils.predict import predict_request_with_json, predict_request_with_file

import nest_asyncio
from pyngrok import ngrok

load_dotenv()

org_id = os.getenv('ORG_ID')
api_token = os.getenv('API_TOKEN')

if api_token is not None and org_id is not None:
    pureml.login(org_id=org_id, api_token=api_token)

predictor = Predictor()
predictor.load_models()

# input_type, input_shape = process_input(input=predictor.input)
# output_type, output_shape = process_output(output=predictor.output)


# Create the app
app = FastAPI()     

# middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True, 
    allow_methods=['*'], 
    allow_headers=['*']
)


@app.post('/predict')
async def predict(request:Request = None, file: Optional[UploadFile] = File(None)):
    if request is None and file is None:
        print('Error in data input format')
        predictions = json.dumps(None)
        return predictions
    

    if request is not None and file is None:
        print("Processing request")
        predictions = await predict_request_with_json(request=request, predictor=predictor)


    if file is not None:
        print("Processing uploaded file")
        predictions = await predict_request_with_file(file=file, predictor=predictor)
        
    return predictions

if __name__ == '__main__':
    ngrok_tunnel = ngrok.connect({PORT})

    # Public URL for fastapi server
    print('Public URL:', ngrok_tunnel.public_url)

    nest_asyncio.apply()

    uvicorn.run(app, host='{HOST}', port={PORT})""".format(
        HOST=fastapi_schema.API_IP_HOST, PORT=fastapi_schema.PORT_FASTAPI
    )

    return api


def create_fastapi_file(
    label, predict_path=None, requirements_path=None, resources_path=None
):
    fastapi_schema = FastAPISchema()

    get_resources(label, resources_path)

    get_predict_file(label, predict_path)

    get_requirements_file(label, requirements_path)

    api = generate_api(label=label)

    with open(fastapi_schema.PATH_FASTAPI_FILE, "w") as api_writer:
        api_writer.write(api)

    api_writer.close()

    print("FastAPI server files are created")


#     print("""
#           API sucessfully created. To run your API, please run the following command
# --> !python <api_name>
#           """)


def run(label, predict_path=None, requirements_path=None):

    create_fastapi_file(
        label, predict_path=predict_path, requirements_path=requirements_path
    )

    interpreter_path = str(sys.executable)

    if os.path.exists(interpreter_path):

        run_command = "'{interpreter_path}' '{api_path}'".format(
            interpreter_path=interpreter_path, api_path=fastapi_schema.PATH_FASTAPI_FILE
        )

        os.system(run_command)
    else:
        print("Interpreter not found at", interpreter_path)

    # app = FastAPI()

    # uvicorn.run(app, host=fastapi_schema.API_IP_HOST, port=fastapi_schema.PORT_FASTAPI)
