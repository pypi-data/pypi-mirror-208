from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict, Set, Union, Tuple
from enum import Enum
from multiprocessing.sharedctypes import Synchronized

from firebird.rabbitmq import RabbitMQ
########################################################################
# Node:         a node of a pipeline
# Sink:         a node without output ports
# Generator:    a node without input ports
# Port:         input port can connect to output port
#
# User do not derive class from Port
########################################################################

DEFAULT_INPUT_PORT_ID   = "input"
DEFAULT_OUTPUT_PORT_ID  = "output"

class PortType(Enum):
    INPUT = 1
    OUTPUT = 2
    
class Node(ABC):
    # Each input port has a unique name among input ports
    # Each output port has a unique name among output ports
    # Sink does not have output ports
    # Source does not have input ports
    def __init__(self, 
        *, 
        id:str,
        pipeline:"Pipeline", 
        input_port_ids:List[str]=[DEFAULT_INPUT_PORT_ID], 
        output_port_ids:List[str]=[DEFAULT_OUTPUT_PORT_ID],
        title:str="",
        description:str="",
    ):
        # validate input port ids and output port ids
        all_port_id_set = set(input_port_ids + output_port_ids)
        if len(all_port_id_set) < len(input_port_ids) + len(output_port_ids):
            raise Exception(f"Duplicate port ids found!")

        self._ports_dict:Dict[str, "Port"] = {}
        self._id:str = id
        self._pipeline:"Pipeline" = pipeline
        self._description:str = description
        if title:
            self._title = title
        else:
            self._title = id
        
        self._input_port_ids:Tuple["Node"] = tuple(input_port_ids)
        self._output_port_ids:Tuple["Node"] = tuple(output_port_ids)

        for port_id in input_port_ids:
            self._ports_dict[port_id] = Port(PortType.INPUT, port_id, self)

        for port_id in output_port_ids:
            self._ports_dict[port_id] = Port(PortType.OUTPUT, port_id, self)
        
        pipeline._add_node(self)
    
    def to_json(self):
        ret = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ports": [port.to_json() for port in self._ports_dict.values()]
        }
        return ret
    
    def __getitem__(self, port_id:str) -> Optional["Port"]:
        return self._get_port(port_id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def pipeline(self) -> "Pipeline":
        return self._pipeline

    @property
    def description(self) -> str:
        return self._description

    @property
    def title(self) -> str:
        return self._title

    @property
    def input_port_ids(self) -> Tuple["Node"]:
        return self._input_port_ids

    @property
    def output_port_ids(self) -> Tuple["Node"]:
        return self._output_port_ids
    
    @property
    def input(self) -> Optional["Port"]:
        # return default input port
        return self._get_port(DEFAULT_INPUT_PORT_ID)
    
    @property
    def output(self) -> Optional["Port"]:
        # return default output port
        return self._get_port(DEFAULT_OUTPUT_PORT_ID)
   
    def _get_port(self, id:str) -> Optional["Port"]:
        # get input port by name
        return self._ports_dict.get(id)

    @abstractmethod
    def on_message(self, port_id:str, data:Any):
        # data arrives form input port with port_id
        pass

    def __lshift__(self, other:Union["Node", "Port", Tuple[Union["Node", "Port"]], List[Union["Node", "Port"]]]):
        # for self << other
        assert other is not None
        if isinstance(other, tuple) or isinstance(other, list):
            for t in other:
                t._connect(self)
            return other

        other._connect(self)
        return other

    def __rshift__(self, other:Union["Node", "Port", Tuple[Union["Node", "Port"]], List[Union["Node", "Port"]]]):
        # for self >> other
        assert other is not None
        if isinstance(other, tuple) or isinstance(other, list):
            for t in other:
                self._connect(t)
            return other

        self._connect(other)
        return other

    def __rlshift__(self, others:Union[Tuple[Union["Node", "Port"]], List[Union["Node", "Port"]]]):
        # for other << self
        for other in others:
            self._connect(other)
        return self

    def __rrshift__(self, others:Union[Tuple[Union["Node", "Port"]], List[Union["Node", "Port"]]]):
        # for other >> self
        for other in others:
            other._connect(self)
        return self

    def _connect(self, other: Union["Node", "Port"]):
        src = self.output
        if isinstance(other, Port):
            dst = other
        else:
            assert isinstance(other, Node)
            dst = other.input
        
        src._connect(dst)
    
    def emit(self, json_data:Any, port_id:str=DEFAULT_OUTPUT_PORT_ID):
        self._get_port(port_id).emit(json_data)
    
    def show_info(self, prefix=""):
        print(f"{prefix}node: id={self.id}")
        for port_id in self.input_port_ids:
            self._get_port(port_id).show_info(prefix=prefix+"    ")
        for port_id in self.output_port_ids:
            self._get_port(port_id).show_info(prefix=prefix+"    ")
    
    def is_generator(self):
        return isinstance(self, Generator)

class Sink(Node):
    def __init__(self, 
        *,
        id:str,
        pipeline:"Pipeline", 
        input_port_ids:List[str]=[DEFAULT_INPUT_PORT_ID],
        title:str="",
        description:str="",
    ):
        super().__init__(
            id=id, 
            pipeline=pipeline, 
            input_port_ids=input_port_ids, 
            output_port_ids=[], 
            title=title,
            description=description
        )

class Generator(Node):
    def __init__(self, 
        *,
        id:str,
        pipeline:"Pipeline", 
        output_port_ids:List[str]=[DEFAULT_OUTPUT_PORT_ID],
        title:str="",
        description:str="",
    ):
        super().__init__(
            id=id, 
            pipeline=pipeline, 
            input_port_ids=[], 
            output_port_ids=output_port_ids,
            title=title,
            description=description
        )

    def on_message(self, name:str, data:Any):
        raise Exception("Generator cannot process data")

    @abstractmethod
    def pump(self, quit_requested: Synchronized):
        """
        Let the source to collect data and emit data

        quit_requested: a boolean shared value
        """
        pass


class Port:
    def __init__(self, type:PortType, id:str, owner:Node):
        self._id:str        = id
        self._type:PortType = type
        self._owner:Node    = owner
        self._connected_ports:Set["Port"] = set()

    def to_json(self):
        ret = {
            "id": self.id,
            "type": self.type.name,
            "connected_ports": [f"{port.owner.id}:{port.id}" for port in self._connected_ports],
        }
        return ret

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> PortType:
        return self._type

    @property
    def owner(self) -> Node:
        return self._owner

    def __lshift__(self, other:Union["Port", Tuple["Port"], List["Port"]]):
        # for self << other
        assert other is not None
        if isinstance(other, tuple) or isinstance(other, list):
            for t in other:
                t._connect(self)
            return other

        other._connect(self)
        return other

    def __rshift__(self, other:Union["Port", List["Port"]]):
        # for self >> other
        assert other is not None
        if isinstance(other, tuple) or isinstance(other, list):
            for t in other:
                self._connect(t)
            return other

        self._connect(other)
        return other

    def __rlshift__(self, others:Union[Tuple["Port"], List["Port"]]):
        # for other << self
        for other in others:
            self._connect(other)
        return self


    def __rrshift__(self, others:Union[Tuple["Port"], List["Port"]]):
        # for other >> self
        for other in others:
            other._connect(self)
        return self

    def _connect(self, other: Union["Node", "Port"]):
        if isinstance(other, Port):
            dst = other
        else:
            assert isinstance(other, Node)
            dst = other.input
        
        if self.type != PortType.OUTPUT:
            raise Exception("Source port MUST be output port!")
        if dst.type != PortType.INPUT:
            raise Exception("Destination port MUST be input port!")

        dst._connected_ports.add(self)
        self._connected_ports.add(dst)

    
    def emit(self, json_data:Any):
        if self.type != PortType.OUTPUT:
            raise Exception("Can only emit data to output port!")

        pipeline = self.owner.pipeline

        for port in self._connected_ports:
            pipeline.mq.produce({
                "from": {
                    "node": self.owner.id,
                    "port": self.id
                },
                "to": {
                    "node": port.owner.id,
                    "port": self.id
                },
                "payload": json_data
            })
    
    def show_info(self, prefix=""):
        t = ",".join([f"{port.owner.id}:{port.id}" for port in self._connected_ports])
        if self.type == PortType.INPUT:
            connect_str = f"from: {t}"
        else:
            connect_str = f"to: {t}"
        print(f"{prefix}port: id={self.id}, type={self.type}, {connect_str}")


    
class Pipeline:
    def __init__(self, *, id:str, mq:Optional[RabbitMQ], title:str="", description:str=""):
        self._id:str = id
        self._description:str = description
        if title:
            self._title:str = title
        else:
            self._title:str = id
        self._mq:RabbitMQ  = mq
        self._node_dict:Dict[str, Node] = {}

    def to_json(self):
        ret = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "nodes": [node.to_json() for node in self._node_dict.values()]
        }
        return ret

    @property
    def id(self) -> str:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @property
    def title(self) -> str:
        return self._title

    @property
    def mq(self) -> Optional[RabbitMQ]:
        return self._mq

    def message_loop(self, quit_requested: Synchronized):
        self.mq.consume(self.on_message, quit_requested)
    
    def on_message(self, envelope):
        node = self._node_dict[envelope['to']['node']]
        node.on_message(
            envelope["to"]["port"],
            envelope["payload"]
        )

    def _add_node(self, node:Node):
        # add a node to the pipeline
        if node.id in self._node_dict:
            raise Exception(f"Node {node.id} already exist!")
        self._node_dict[node.id] = node
    
    
    def __getitem__(self, node_id:str) -> Optional[Node]:
        return self._node_dict.get(node_id)

    @property
    def nodes(self):
        return tuple(self._node_dict.values())

    def show_info(self, prefix=""):
        print(f"{prefix}pipeline: id={self.id}")
        for node_id, node in self._node_dict.items():
            assert node.id == node_id
            node.show_info(prefix=prefix+"    ")

