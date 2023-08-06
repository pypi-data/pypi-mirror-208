#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import argparse
import importlib
import os
import sys
import json

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
}

# logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline Tool'
    )
    parser.add_argument(
        "action", type=str, help="Specify action",
        choices=['register', 'unregister', 'list', 'execute', 'stop'],
        nargs=1
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Specify if you want to show debug logs",
    )
    parser.add_argument(
        "-cd", "--config-dir", type=str, required=False,
        help="Configuration directory"
    )
    parser.add_argument(
        "-pmn", "--pipeline-module-name", type=str, required=False,
        help="Pipeline module name"
    )
    parser.add_argument(
        "-pid", "--pipeline-id", type=str, required=False, help="pipeline ID"
    )
    parser.add_argument(
        "-wc", "--worker-count", type=int, default=1, required=False,
        help="Worker count"
    )
    parser.add_argument(
        "-dhn", "--docker-host-name", type=str, required=False,
        help="Docker host name"
    )
    parser.add_argument(
        "-dcn", "--docker-container-name", type=str, required=False,
        help="Docker container name"
    )
    parser.add_argument(
        "-eid", "--executor-id", type=str, required=False, help="Executor ID"
    )
    args = parser.parse_args()
    action = args.action[0]

    if args.debug:
        logging.config.dictConfig(LOG_CONFIG)
    
    config_dir = args.config_dir if args.config_dir else os.path.expanduser("~/.firebird")
    config_filename = os.path.join(config_dir, "config.json")
    if not os.path.isfile(config_filename):
        print(f"Unable to find config file from {config_filename}")
        sys.exit(1)

    with open(config_filename, "rt") as f:
        config = json.load(f)

    impl = importlib.import_module("firebird.cmd_tools.pipeline_impl")

    if action == "register":
        impl.register_command(config, args.pipeline_module_name)
    if action == "unregister":
        impl.unregister_command(config, args.pipeline_id)
    elif action == "list":
        impl.list_command(config)
    elif action == "execute":
        impl.execute_command(config, args.docker_host_name, args.docker_container_name, args.pipeline_id, args.worker_count)
    elif action == "stop":
        impl.stop_command(config, args.pipeline_id, args.executor_id)
        


if __name__ == '__main__':
    main()
