import os
from django.http import JsonResponse
from django.http  import HttpRequest, HttpResponse
from django.conf import settings
from firebird import zkdb
import tempfile
import xml.dom.minidom
import graphviz

def list_pipelines(request:HttpRequest)->HttpResponse:
    with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
        pipelines = db.get_pipelines()
    return JsonResponse({
        "pipelines": pipelines
    })

def get_pipeline(request:HttpRequest, pipeline_id:str)->HttpResponse:
    with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
        pipeline = db.get_pipeline(pipeline_id)

    filename = None
    svg_filename = None
    with tempfile.NamedTemporaryFile(prefix="firebird-svg-", delete=False) as f:
        filename = f.name
        svg_filename = f"{filename}.svg"

    try:
        edges = set()
        g = graphviz.Digraph(format="svg")
        for node in pipeline["info"]["nodes"]:
            g.node(node['id'], node['id'])

            for port in node["ports"]:
                if port["type"] == "OUTPUT":
                    for connected_port in port["connected_ports"]:
                        next_node_id, _ = connected_port.split(":")
                        edges.add((node["id"], next_node_id))
        for src_node_id, next_node_id in edges:
            g.edge(src_node_id, next_node_id)
        g.render(filename=filename)

        doc = xml.dom.minidom.parse(svg_filename)
        svg = doc.documentElement.toxml()
    finally:
        for fn in [filename, svg_filename]:
            if os.path.isfile(fn):
                os.remove(fn)

    return JsonResponse({
        "pipeline": pipeline,
        "svg": svg
    })
