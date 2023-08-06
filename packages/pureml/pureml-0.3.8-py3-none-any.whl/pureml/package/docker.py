import os
import docker
from .fastapi import create_fastapi_file
from pureml.schema import FastAPISchema, PredictSchema, DockerSchema
import string, random
from pureml.utils.env import generate_env_dict, validate_env_docker

prediction_schema = PredictSchema()
fastapi_schema = FastAPISchema()
docker_schema = DockerSchema()


def generate_sys_commands(sys_commands):
    commands = "\nRUN apt update\n"
    if len(sys_commands) > 0:
        sys_commands = ["RUN " + i for i in sys_commands]
        commands += "\n".join(sys_commands)

    return commands


def create_docker_file(sys_commands):
    # os.makedirs(PATH_DOCKER_DIR, exist_ok=True)
    os.makedirs(prediction_schema.paths.PATH_PREDICT_DIR, exist_ok=True)

    req_pos = prediction_schema.PATH_PREDICT_REQUIREMENTS.rfind(
        prediction_schema.REQUIREMENTS_NAME
    )
    req_path = prediction_schema.PATH_PREDICT_REQUIREMENTS[req_pos:]

    api_pos = fastapi_schema.PATH_FASTAPI_FILE.rfind(
        prediction_schema.paths.PATH_PREDICT_DIR_RELATIVE
    )
    api_path = fastapi_schema.PATH_FASTAPI_FILE[api_pos:]

    commands = generate_sys_commands(sys_commands=sys_commands)

    docker = """
    
FROM {BASE_IMAGE}

{commands}

RUN mkdir -p {PREDICT_DIR}

WORKDIR {PREDICT_DIR}

ADD . {PREDICT_DIR}

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r {REQUIREMENTS_PATH}

RUN pip install fastapi uvicorn python-multipart

RUN pip install pureml

EXPOSE {PORT}
CMD ["python", "{API_PATH}"]    
""".format(
        BASE_IMAGE=docker_schema.BASE_IMAGE_DOCKER,
        PORT=docker_schema.PORT_DOCKER,
        PREDICT_DIR=prediction_schema.paths.PATH_PREDICT_DIR_RELATIVE,
        API_PATH=api_path,
        REQUIREMENTS_PATH=req_path,
        commands=commands,
    )

    with open(docker_schema.PATH_DOCKER_IMAGE, "w") as docker_file:
        docker_file.write(docker)

    docker_yaml = """version: '3'

services:
  prediction:
    build: .
    container_name: "{CONTAINER_NAME}"
    expose:
      - "{DOCKER_PORT}"
    ports:
      - "{HOST_PORT}:{DOCKER_PORT}"
    
    """.format(
        DOCKER_PORT=docker_schema.PORT_DOCKER,
        HOST_PORT=docker_schema.PORT_HOST,
        CONTAINER_NAME="pureml_prediction",
    )

    with open(docker_schema.PATH_DOCKER_CONFIG, "w") as docker_yaml_file:
        docker_yaml_file.write(docker_yaml)


def create_docker_image(label):
    # if image_tag is None:
    # image_tag = "pureml_docker_image"
    label = label.replace(" ", "")

    image_repository = label.split(":", 1)[0]
    image_tag = label.split(":", 1)[1].replace(":", "-")

    # random_value = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    # image_tag = "-".join([image_tag, random_value])

    image_tag = ":".join([image_repository, image_tag])

    client = docker.from_env()

    docker_file_path_relative = docker_schema.PATH_DOCKER_IMAGE.split(os.path.sep)[-1]
    # print(docker_schema.paths.PATH_PREDICT_DIR)
    # print(docker_file_path_relative)
    # print(image_tag)

    try:
        image, build_log = client.images.build(
            path=docker_schema.paths.PATH_PREDICT_DIR,
            dockerfile=docker_file_path_relative,
            tag=image_tag,
            nocache=True,
            rm=True,
        )

        print("Docker image is created.")
        print("Tag: ", image_tag)
        print("Image Long Id:", image.id)
        print("Image Short Id: ", image.short_id)

    except Exception as e:
        print(e)
        image = None
        build_log = None

    return image, build_log, image_tag


def run_docker_container(image, runtime, gpu_ids, host_port, docker_port, env_dict):
    client = docker.from_env()
    name = image.tags[0].replace(":", "-")

    random_value = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    name = "-".join([name, random_value])

    docker_port = "{p}/tcp".format(p=docker_port)

    # print("docker_port", docker_port)
    container_args = {
        "image": image,
        "ports": {docker_port: host_port},
        "detach": True,
        "auto_remove": True,
        "name": name,
        "runtime": runtime,
        "environment": env_dict,
    }

    if len(gpu_ids) != 0:
        gpu_ids = [str(id) for id in gpu_ids]
        container_args["device_requests"] = [
            docker.types.DeviceRequest(device_ids=gpu_ids, capabilities=[["gpu"]])
        ]

    container = client.containers.run(**container_args)

    # container = client.containers.run(
    #     image=image,
    #     ports={docker_port: docker_schema.PORT_HOST},
    #     detach=True,
    #     name=name,
    #     runtime=runtime,
    # )

    return container


def create(
    label,
    # org_id,
    # access_token,
    env_path,
    runtime=None,
    gpu_ids=[],
    port=None,
    predict_path=None,
    requirements_path=None,
    sys_commands=[],
):

    env_dict = generate_env_dict(env_path=env_path)
    env_valid = validate_env_docker(env_dict=env_dict)

    if not env_valid:
        return None

    create_fastapi_file(
        label=label, predict_path=predict_path, requirements_path=requirements_path
    )

    create_docker_file(sys_commands=sys_commands)

    image, build_log, image_tag = create_docker_image(label=label)

    if image is not None:

        if port is None:
            host_port = docker_schema.PORT_HOST
        else:
            host_port = port

        docker_port = docker_schema.PORT_DOCKER

        container = run_docker_container(
            image=image,
            runtime=runtime,
            gpu_ids=gpu_ids,
            host_port=host_port,
            docker_port=docker_port,
            env_dict=env_dict,
        )

        print("Created Docker container")
        print("Container Name: ", container.name)
        print("Container Long Id: ", container.id)
        print("Container id: ", container.short_id)

        print(
            "Prediction requests can be forwarded to {ip}:{p}/predict".format(
                ip=docker_schema.API_IP_HOST, p=host_port
            )
        )
    else:
        print("Failed to create the container")
        print("Build Log")
        print(build_log)


def get(container_id):

    client = docker.from_env()

    container = client.containers.get(container_id)

    return container


def stop(container_id):

    client = docker.from_env()

    container = client.containers.get(container_id)

    container.stop()
