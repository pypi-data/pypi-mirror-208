#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import argparse
import importlib

import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline executor'
    )
    parser.add_argument(
        "-cd", "--config-dir", type=str, default=os.path.expanduser("~/.firebird"), required=False,
        help="Configuration directory"
    )
    parser.add_argument(
        "-pid", "--pipeline-id", type=str, required=True, help="pipeline ID"
    )
    parser.add_argument(
        "-dhn", "--docker-host-name", type=str, required=True, help="docker host name"
    )
    parser.add_argument(
        "-dcn", "--docker-container-name", type=str, required=True, help="docker container name"
    )
    parser.add_argument(
        "-wc", "--worker-count", type=int, default=1, required=False,
        help="Worker count"
    )
    args = parser.parse_args()

    # config log
    log_config_filename = os.path.join(args.config_dir, "log_config.json")
    if os.path.isfile(log_config_filename):
        with open(log_config_filename, "rt") as f:
            LOG_CONFIG = json.load(f)
    else:
        LOG_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                    "stream"  : "ext://sys.stdout"
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
            "loggers": {
                "pika": {
                    "handlers": ["console"],
                    "level":    "WARNING",
                    "propagate": False
                },
                "kazoo": {
                    "handlers": ["console"],
                    "level":    "WARNING",
                    "propagate": False
                }
            }
        }
    logging.config.dictConfig(LOG_CONFIG)

    config_filename = os.path.join(args.config_dir, "config.json")
    if not os.path.isfile(config_filename):
        print(f"Unable to find config file from {config_filename}")
        sys.exit(1)

    with open(config_filename, "rt") as f:
        config = json.load(f)
    
    impl = importlib.import_module("firebird.cmd_tools.executor_impl")
    impl.execute_pipeline(
        config, 
        pipeline_id=args.pipeline_id, 
        worker_count=args.worker_count, 
        docker_host_name=args.docker_host_name, 
        docker_container_name=args.docker_container_name
    )


if __name__ == '__main__':
    main()
