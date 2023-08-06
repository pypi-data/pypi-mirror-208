import json
import os
from datetime import datetime
from contextlib import contextmanager
from kazoo.client import KazooClient

@contextmanager
def zkdb(**kwargs):
    zk = KazooClient(**kwargs)
    db = ZKDatabase(zk)
    zk.start()
    try:
        yield db
    finally:
        zk.stop()
        zk.close()

class ZKDatabase:
    """
    Manage zookeeper database
    """
    def __init__(self, zk):
        self.zk = zk
    
    def register_pipeline(self, pipeline_id:str, pipeline_module_name:str, pipeline_info:str):
        """
        Register a pipeline
        """
        self.zk.ensure_path("/pipelines")
        pipeline_path = f"/pipelines/{pipeline_id}"
        if self.zk.exists(pipeline_path):
            raise Exception(f"Pipeline {pipeline_id} is already registered!")
        
        self.zk.ensure_path(pipeline_path)
        self.zk.create(f"{pipeline_path}/info", json.dumps(pipeline_info).encode("utf-8"))
        self.zk.create(f"{pipeline_path}/module", pipeline_module_name.encode("utf-8"))

    def unregister_pipeline(self, pipeline_id:str):
        """
        Unregister a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.zk.exists(pipeline_path):
            raise Exception(f"Pipeline {pipeline_id} is not yet registered!")
        
        executors_path = f"{pipeline_path}/executors"
        if self.zk.exists(executors_path) and len(self.zk.get_children(executors_path)) > 0:
            raise Exception(f"Pipeline {pipeline_id} has executors!")
        
        self.zk.delete(pipeline_path, recursive=True)

    def get_pipelines(self) -> dict:
        """
        Get information for all pipelines
        """
        if not self.zk.exists("/pipelines"):
            return []
        return [
            self.get_pipeline(pipeline_id) for pipeline_id in self.zk.get_children("/pipelines")
        ]

    def get_executor(self, pipeline_id:str, executor_id:str) -> dict:
        """
        Get information for an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.zk.exists(executor_path):
            return None
        v, _ = self.zk.get(f"{executor_path}/info")
        executor_info = json.loads(v.decode("utf-8"))
        executor_info['id'] = executor_id
        v, _ = self.zk.get(f"{executor_path}/stop")
        stop = v == b'1'
        return {
            "info": executor_info,
            "stop": stop
        }

    def get_executor_stop(self, pipeline_id:str, executor_id:str) -> bool:
        """
        Check if stop is requested for an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        v, _ = self.zk.get(f"{executor_path}/stop")
        return v == b'1'

    def get_pipeline(self, pipeline_id:str) -> dict:
        """
        Get information for a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.zk.exists(pipeline_path):
            return None

        v, _ = self.zk.get(f"{pipeline_path}/info")
        pipeline_info = json.loads(v.decode("utf-8"))
        v, _ = self.zk.get(f"{pipeline_path}/module")
        module = v.decode("utf-8")

        executor_ids_path = f"/pipelines/{pipeline_id}/executors"
        executors = []
        if self.zk.exists(executor_ids_path):
            executors = [
                self.get_executor(pipeline_id, executor_id) for executor_id in self.zk.get_children(executor_ids_path)
            ]
        
        return {
            "info": pipeline_info,
            "module": module,
            "executors": executors
        }


    def register_executor(
        self, 
        pipeline_id:str, 
        executor_id:str, 
        *, 
        docker_host_name:str, 
        docker_container_name:str, 
        worker_count:int
    ):
        """
        Register an executor
        """
        if not self.zk.exists(f"/pipelines/{pipeline_id}"):
            raise Exception(f"Pipeline {pipeline_id} does not exist!")
    
        executors_path = f"/pipelines/{pipeline_id}/executors"
        self.zk.ensure_path(executors_path)

        executor_path = f"{executors_path}/{executor_id}"
        if self.zk.exists(executor_path):
            raise Exception(f"Executor {executor_id} already exist!")
        
        self.zk.ensure_path(executor_path)

        executor_info = {
            "docker_host_name": docker_host_name,
            "docker_container_name": docker_container_name,
            "worker_count": worker_count,
            "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid(),
        }
        self.zk.create(f"{executor_path}/info", json.dumps(executor_info).encode("utf-8"))
        self.zk.create(f"{executor_path}/stop", b'0')

    def watch_executor(self, pipeline_id:str, executor_id:str, callback):
        """
        Watch if stop is requested on an executor
        """
        def watcher(event):
            if event.type == "CHANGED":
                stop = self.get_executor_stop(pipeline_id, executor_id)
                if stop:
                    callback()
                else:
                    # keep watching...
                    self.watch_executor(pipeline_id, executor_id, callback)
            else:
                # keep watching...
                self.watch_executor(pipeline_id, executor_id, callback)

        stop_path = f"/pipelines/{pipeline_id}/executors/{executor_id}/stop"
        if self.zk.exists(stop_path):
            self.zk.get(stop_path, watcher)
        

    def unregister_executor(self, pipeline_id:str, executor_id:str):
        """
        Unregister an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.zk.exists(executor_path):
            raise Exception(f"Executor {executor_id} does not exist!")
        self.zk.delete(executor_path, recursive=True)

    def stop_executor(self, pipeline_id:str, executor_id:str):
        """
        Request stop of an executor.
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.zk.exists(executor_path):
            raise Exception(f"Executor {executor_id} does not exist!")
    
        self.zk.set(f"{executor_path}/stop", b'1')
