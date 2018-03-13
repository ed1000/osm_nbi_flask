from flask import Blueprint

ns_lcm_op_occs = Blueprint('nslcm_v1_ns_lcm_op_occs', __name__)

@ns_lcm_op_occs.route('/', methods=['GET'])
def get_ns_lcm_op_occs():
    return "GET from /osm/nslcm/v1/ns_lcm_op_occs"

@ns_lcm_op_occs.route('/', methods=['POST'])
def post_ns_lcm_op_occs():
    return "POST from /osm/nslcm/v1/ns_lcm_op_occs"

@ns_lcm_op_occs.route('/<ns_lcm_op_occ_id>', methods=['GET'])
def get_ns_lcm_op_occ_id(ns_lcm_op_occ_id):
    return "GET from /osm/nslcm/v1/ns_lcm_op_occs/{}".format(ns_lcm_op_occ_id)

@ns_lcm_op_occs.route('/<ns_lcm_op_occ_id>', methods=['DELETE'])
def delete_ns_lcm_op_occ_id(ns_lcm_op_occ_id):
    return "DELETE from /osm/nslcm/v1/ns_lcm_op_occs/{}".format(ns_lcm_op_occ_id)

@ns_lcm_op_occs.route('/<ns_lcm_op_occ_id>', methods=['PATCH'])
def patch_ns_lcm_op_occ_id(ns_lcm_op_occ_id):
    return "PATCH from /osm/nslcm/v1/ns_lcm_op_occs/{}".format(ns_lcm_op_occ_id)