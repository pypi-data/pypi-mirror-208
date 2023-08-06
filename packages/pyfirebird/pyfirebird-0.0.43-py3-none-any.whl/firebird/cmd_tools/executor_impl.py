#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict
import logging

###################################################################
# the main process need to monitor child process
# - if main process got SIGTERM (killed), it will set quit_requested to True
#   this variable has been shared with child processes, so child process can check it and quit
#   accordingly
# - if a child process is terminated. The main process knows it
#   TODO: the main process can check the child process exit code and retry it if needed
# - if a child process got SIGTERM, it will quit.
###################################################################
logger = logging.getLogger(__name__)

import importlib
import signal
import time
from multiprocessing import Process, Value
from collections import deque
from uuid import uuid4
from firebird import zkdb

from firebird.rabbitmq import get_connection, RabbitMQ

__APP_CONTEXT = {
    'quit_requested': Value('b', False)
}

__WORKER_CONTEXT = {
    'quit_requested': False
}
    
def __request_main_shutdown(signal_umber, frame):
    _, _ = signal_umber, frame
    __APP_CONTEXT['quit_requested'].value = True
    logger.info("main: Got SIGTERM")

def __request_worker_shutdown(signal_umber, frame):
    _, _ = signal_umber, frame
    __WORKER_CONTEXT['quit_requested'] = True
    logger.info("worker: Got SIGTERM")


def worker_main(config:dict, pipeline_module_name:str, pipeline_id:str, node_id, quit_requested):
    signal.signal(signal.SIGTERM, __request_worker_shutdown)  # regular kill command

    mq = RabbitMQ(
        connection = get_connection(**config["rabbitmq"]),
        topic = pipeline_id
    )
    pipeline = importlib.import_module(pipeline_module_name).get_pipeline(mq)
    
    if node_id is not None:
        # this is for generator
        generator = pipeline[node_id]
        generator.pump(quit_requested)
        return
    
    # otherwise, this is for message processing
    pipeline.message_loop(quit_requested)

def execute_pipeline(
    config:dict, 
    *, 
    pipeline_id:str, 
    worker_count:int, 
    docker_host_name:str, 
    docker_container_name:str
):
    logger.info(f"execute_pipeline: enter")
    logger.info(f"execute_pipeline: pipeline_id={pipeline_id}, worker_count={worker_count}, docker_host_name={docker_host_name}, docker_container_name={docker_container_name}")
    zk_config = config['zookeeper']

    with zkdb(**zk_config) as db:
        pipeline = db.get_pipeline(pipeline_id)
        pipeline_module_name = pipeline['module']
        logger.info(f"execute_pipeline: pipeline_module_name={pipeline_module_name}")

        # try to import the pipeline
        pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
        logger.info(f"execute_pipeline: pipeline acquired")

        executor_id = str(uuid4())
        logger.info(f"execute_pipeline: executor_id={executor_id}")
        db.register_executor(
            pipeline_id, 
            executor_id, 
            docker_host_name=docker_host_name, 
            docker_container_name=docker_container_name, 
            worker_count=worker_count
        )
        logger.info(f"execute_pipeline: executor_id registered")

    active_processes = deque()
    terminated_processes = deque()
    signal.signal(signal.SIGTERM, __request_main_shutdown)  # regular kill command
    logger.info("Started")
    for node in pipeline.nodes:
        if node.is_generator():
            p = Process(
                target=worker_main,
                args=((config, pipeline_module_name, pipeline_id, node.id, __APP_CONTEXT['quit_requested']))
            )
            p.start()
            active_processes.append(p)
    for i in range(worker_count):
        p = Process(
            target=worker_main,
            args=((config, pipeline_module_name, pipeline_id, None, __APP_CONTEXT['quit_requested']))
        )
        p.start()
        active_processes.append(p)

    logger.info(f"execute_pipeline: all worker started")

    def watch_stop():
        logger.info(f"execute_pipeline: stop requested!")
        __APP_CONTEXT['quit_requested'].value = True

    
    with zkdb(**zk_config) as db:
        db.watch_executor(pipeline_id, executor_id, watch_stop)
        while True:
            if len(active_processes) == 0:
                break
            tmp = active_processes
            active_processes = deque()
            for p in tmp:
                if p.is_alive():
                    active_processes.append(p)
                else:
                    p.join()
                    logger.info(f"execute_pipeline: pid={p.pid} is terminated!")
                    terminated_processes.append(p)
            time.sleep(1)
        logger.info(f"execute_pipeline: all worker stopped")
        db.unregister_executor(pipeline_id, executor_id)

    logger.info(f"execute_pipeline: executor {executor_id} unregistered")
    logger.info(f"execute_pipeline: exit")

