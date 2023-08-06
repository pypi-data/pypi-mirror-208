#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict, Callable
import logging
import logging.config
import importlib
from uuid import uuid4
from firebird.rabbitmq import get_connection, RabbitMQ
from firebird import zkdb
import docker

logger = logging.getLogger(__name__)

def register_command(config:dict, pipeline_module_name:str):
    pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
    pipeline_info = pipeline.to_json()

    mq = RabbitMQ(
        connection = get_connection(**config["rabbitmq"]),
        topic = pipeline.id
    )
    # create rabbitmq topic, etc
    mq.initialize()

    with zkdb(**config['zookeeper']) as db:
        db.register_pipeline(pipeline.id, pipeline_module_name, pipeline_info)

def unregister_command(config:dict, pipeline_id:str):
    with zkdb(**config['zookeeper']) as db:
        db.unregister_pipeline(pipeline_id)

def list_command(config):
    with zkdb(**config['zookeeper']) as db:
        pipelines = db.get_pipelines()

    for pipeline in pipelines:
        print(f"{pipeline['info']['id']}:")
        print(f"    module: {pipeline['module']}")
        if len(pipeline["executors"]) == 0:
            print("    executors: None")
        else:
            print("    executors:")
            for executor in pipeline["executors"]:
                executor_info = executor["info"]
                print(f"        {executor_info['id']}:")
                print(f"            docker_host_name      = {executor_info['docker_host_name']}")
                print(f"            docker_container_name = {executor_info['docker_container_name']}")
                print(f"            worker_count          = {executor_info['worker_count']}")
                print(f"            start_time            = {executor_info['start_time']}")
                print(f"            pid                   = {executor_info['pid']}")

def stop_command(config:dict, pipeline_id:str, executor_id:str):
    with zkdb(**config['zookeeper']) as db:
        db.stop_executor(pipeline_id, executor_id)

def execute_command(config:dict, docker_host_name:str, docker_container_name:str, pipeline_id:str, worker_count:int):
    docker_handler_module = config["docker_handler_module"]
    docker_handler = importlib.import_module(docker_handler_module)

    docker_client = docker.DockerClient(base_url=f"ssh://{docker_host_name}:22", use_ssh_client=True)
    try:
        docker_handler.launch_executor(docker_client, docker_host_name, docker_container_name, pipeline_id, worker_count)
    finally:
        docker_client.close()
