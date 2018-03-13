from flask import Blueprint

ns_instances = Blueprint('nslcm_v1_ns_instances', __name__)

@ns_instances.route('/', methods=['GET'])
def get_ns_instances():
    return "GET from /osm/nslcm/v1/ns_instances"

@ns_instances.route('/', methods=['POST'])
def post_ns_instances():
    return "POST from /osm/nslcm/v1/ns_instances"

@ns_instances.route('/<ns_instance_id>', methods=['GET'])
def get_ns_instance_id(ns_instance_id):
    return "GET from /osm/nslcm/v1/ns_instances/{}".format(ns_instance_id)

@ns_instances.route('/<ns_instance_id>', methods=['DELETE'])
def delete_ns_instance_id(ns_instance_id):
    return "DELETE from /osm/nslcm/v1/ns_instances/{}".format(ns_instance_id)
