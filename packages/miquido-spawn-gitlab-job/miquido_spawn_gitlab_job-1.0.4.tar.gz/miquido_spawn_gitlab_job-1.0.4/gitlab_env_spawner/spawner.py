import json
import os
from functools import reduce

import boto3


def __map_container_files(s):
    with open(s[1], 'r') as f:
        return f.read()


def spawn():
    lb = boto3.client('lambda')
    additional_containers = list(filter(lambda x: x[0][0:11] == 'DD_SERVICE_', os.environ.items()))
    additional_containers = list(map(__map_container_files, additional_containers))

    environment_variables = list(filter(lambda x: x[0][0:3] == 'DD_', os.environ.items()))
    environment_variables = list(map(lambda x: (x[0][3:], x[1]), environment_variables))
    environment_variables = reduce(lambda res, x: {**res, **{x[0]: x[1]}}, environment_variables, {})

    function_name = os.getenv('SPAWNER_FUNCTION_NAME', 'prod-dynamic-containers-lambda-terraform')
    name = f"{os.getenv('CI_PROJECT_NAME')}-{os.getenv('CI_COMMIT_REF_SLUG')}"
    image = os.getenv('CI_REGISTRY_IMAGE')
    tag = f"{os.getenv('CI_PIPELINE_ID')}-{os.getenv('CI_COMMIT_SHORT_SHA')}"
    gitlab_user = os.getenv('CI_DEPLOY_USER')
    gitlab_password = os.getenv('CI_DEPLOY_PASSWORD')
    payload = {
        'name': name,
        'image': image,
        'tag': tag,
        'gitlab_user': gitlab_user,
        'gitlab_password': gitlab_password,
        'service_envs': environment_variables,
        'additional_containers': additional_containers
    }

    res = lb.invoke(FunctionName=function_name,
                    Payload=bytes(json.dumps(payload), 'utf-8'))
    print(res)
