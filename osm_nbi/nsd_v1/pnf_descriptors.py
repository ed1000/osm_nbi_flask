from flask import Blueprint

pnf_descriptors = Blueprint('nsd_v1_pnf_descriptors', __name__)

@pnf_descriptors.route('/', methods=['GET'])
def get_pnf_descriptors():
    return "GET from /osm/nsd/v1/pnf_descriptors"

@pnf_descriptors.route('/', methods=['POST'])
def post_pnf_descriptors():
    return "POST from /osm/nsd/v1/pnf_descriptors"

@pnf_descriptors.route('/<pnfd_info_id>', methods=['GET'])
def get_pnf_descriptor_id(pnfd_info_id):
    return "GET from /osm/nsd/v1/pnf_descriptors/{}".format(pnfd_info_id)

@pnf_descriptors.route('/<pnfd_info_id>', methods=['DELETE'])
def delete_pnf_descriptor_id(pnfd_info_id):
    return "DELETE from /osm/nsd/v1/pnf_descriptors/{}".format(pnfd_info_id)

@pnf_descriptors.route('/<pnfd_info_id>', methods=['PATCH'])
def patch_pnf_descriptor_id(pnfd_info_id):
    return "PATCH from /osm/nsd/v1/pnf_descriptors/{}".format(pnfd_info_id)

@pnf_descriptors.route('/<pnfd_info_id>/pnfd_content', methods=['GET'])
def get_pnfd_content(pnfd_info_id):
    return "GET from /osm/nsd/v1/pnf_descriptors/{}/pnfd_content".format(pnfd_info_id)

@pnf_descriptors.route('/<pnfd_info_id>/pnfd_content', methods=['PUT'])
def put_pnfd_content(pnfd_info_id):
    return "DELETE from /osm/nsd/v1/pnf_descriptors/{}/pnfd_content".format(pnfd_info_id)