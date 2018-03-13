from flask import Blueprint

ns_descriptors = Blueprint('nsd_v1_ns_descriptors', __name__)

@ns_descriptors.route('/', methods=['GET'])
def get_ns_descriptors():
    return "GET from /osm/nsd/v1/ns_descriptors"

@ns_descriptors.route('/', methods=['POST'])
def post_ns_descriptors():
    return "POST from /osm/nsd/v1/ns_descriptors"

@ns_descriptors.route('/<nsd_info_id>', methods=['GET'])
def get_ns_descriptor_id(nsd_info_id):
    return "GET from /osm/nsd/v1/ns_descriptors/{}".format(nsd_info_id)

@ns_descriptors.route('/<nsd_info_id>', methods=['DELETE'])
def delete_ns_descriptor_id(nsd_info_id):
    return "DELETE from /osm/nsd/v1/ns_descriptors/{}".format(nsd_info_id)

@ns_descriptors.route('/<nsd_info_id>', methods=['PATCH'])
def patch_ns_descriptor_id(nsd_info_id):
    return "PATCH from /osm/nsd/v1/ns_descriptors/{}".format(nsd_info_id)

@ns_descriptors.route('/<nsd_info_id>/nsd_content', methods=['GET'])
def get_nsd_content(nsd_info_id):
    return "GET from /osm/nsd/v1/ns_descriptors/{}/nsd_content".format(nsd_info_id)

@ns_descriptors.route('/<nsd_info_id>/nsd_content', methods=['PUT'])
def put_nsd_content(nsd_info_id):
    return "PUT from /osm/nsd/v1/ns_descriptors/{}/nsd_content".format(nsd_info_id)
