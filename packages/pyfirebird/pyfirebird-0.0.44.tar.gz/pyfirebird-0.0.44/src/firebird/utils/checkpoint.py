from typing import List, Any, Optional
from datetime import datetime, timedelta
from copy import copy, deepcopy

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class CheckPointTrackingObject:
    def __init__(self, id:str, ts:datetime, payload:Any=None):
        self.id = id
        self.ts = ts
        self.payload = deepcopy(payload)
    
    def to_json(self):
        return {
            "id": self.id,
            "ts": self.ts.strftime(TIME_FORMAT),
            "payload": deepcopy(self.payload)
        }
    
    @classmethod
    def from_json(cls, json_payload):
        return cls(
            id=json_payload["id"], 
            ts=datetime.strptime(json_payload["ts"], TIME_FORMAT), 
            payload=json_payload.get("payload")
        )
    
    def clone(self):
        return CheckPointTrackingObject(id=self.id, ts=self.ts, payload=self.payload)


class CheckPoint:
    def __init__(
        self, 
        *,
        window_start:datetime, 
        window_end: datetime, 
        max_window_length: int,
        max_step_length:int,
        min_step_length:int,
        objects: List[CheckPointTrackingObject]=[]
    ):
        assert window_start <= window_end
        assert max_window_length > 0
        assert min_step_length > 0
        assert max_step_length > 0
        assert min_step_length <= max_step_length

        self.window_start       = window_start
        self.window_end         = window_end
        self.max_window_length  = timedelta(seconds=max_window_length)
        self.max_step_length    = timedelta(seconds=max_step_length)
        self.min_step_length    = timedelta(seconds=min_step_length)
        self.objects            = copy(objects)
        self.object_ids         = set([obj.id for obj in self.objects])

    
    @classmethod
    def from_json(cls, json_payload:Optional[dict]=None):
        return cls(
            window_start        = datetime.strptime(json_payload["window_start"], TIME_FORMAT),
            window_end          = datetime.strptime(json_payload["window_end"], TIME_FORMAT),
            max_window_length   = json_payload["max_window_length"],
            max_step_length     = json_payload["max_step_length"],
            min_step_length     = json_payload["min_step_length"],
            objects             = [
                CheckPointTrackingObject.from_json(obj) for obj in json_payload.get("objects", [])
            ]
        )

    def to_json(self):
        json_payload = {
            "window_start"      : self.window_start.strftime(TIME_FORMAT),
            "window_end"        : self.window_end.strftime(TIME_FORMAT),
            "max_window_length" : int(self.max_window_length.total_seconds()),
            "max_step_length"   : int(self.max_step_length.total_seconds()),
            "min_step_length"   : int(self.min_step_length.total_seconds()),
            "objects"           : [obj.to_json() for obj in self.objects]
        }
        return json_payload
    
    def can_advance(self, new_window_end:datetime) -> bool:
        return new_window_end >= self.window_end + self.min_step_length

    def advance(
        self, 
        new_window_end:datetime, 
        objects_to_add:List[CheckPointTrackingObject]
    ) -> List[CheckPointTrackingObject]:
        if not self.can_advance(new_window_end):
            return None

        # one move cannot step longer than max_step_length
        effective_new_window_end = min(
            new_window_end, 
            self.window_end + self.max_step_length
        )

        obj_added = []
        for obj in objects_to_add:
            if obj.ts < self.window_start or obj.ts >= effective_new_window_end:
                # object not belong to the checkpoint window, ignore it
                continue
            if obj.id in self.object_ids:
                # object id already exist, ignore it
                continue
            self.objects.append(obj.clone())
            self.object_ids.add(obj.id)
            obj_added.append(obj)
        
        self.window_start = max(
            self.window_start,
            effective_new_window_end - self.max_window_length
        )
        self.window_end = effective_new_window_end
        self.objects = [obj for obj in self.objects if obj.ts >= self.window_start]
        self.object_ids     = set([obj.id for obj in self.objects])
        return obj_added
