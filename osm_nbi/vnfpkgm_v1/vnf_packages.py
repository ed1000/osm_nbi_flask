from flask import Blueprint

vnf_packages = Blueprint('vnfpkgm_v1_vnf_packages', __name__)

@vnf_packages.route('/', methods=['GET'])
def get_vnf_packages():
    return "GET from /osm/vnfpkgm/v1/vnf_packages"

@vnf_packages.route('/', methods=['POST'])
def post_vnf_packages():
    return "POST from /osm/vnfpkgm/v1/vnf_packages"

@vnf_packages.route('/<vnf_pkg_id>', methods=['GET'])
def get_vnf_package_id(vnf_pkg_id):
    return "GET from /osm/vnfpkgm/v1/vnf_packages/{}".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>', methods=['DELETE'])
def delete_vnf_package_id(vnf_pkg_id):
    return "DELETE from /osm/vnfpkgm/v1/vnf_packages/{}".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>', methods=['PATCH'])
def patch_vnf_package_id(vnf_pkg_id):
    return "PATCH from /osm/vnfpkgm/v1/vnf_packages/{}".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/vnfd', methods=['GET'])
def get_vnf_package_id_vnfd(vnf_pkg_id):
    return "GET from /osm/vnfpkgm/v1/vnf_packages/{}/vnfd".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/vnfd', methods=['POST'])
def post_vnf_package_id_vnfd(vnf_pkg_id):
    return "POST from /osm/vnfpkgm/v1/vnf_packages/{}/vnfd".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/package_content', methods=['GET'])
def get_vnf_package_id_package_content(vnf_pkg_id):
    return "GET from /osm/vnfpkgm/v1/vnf_packages/{}/package_content".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/package_content', methods=['PUT'])
def put_vnf_package_id_package_content(vnf_pkg_id):
    return "PUT from /osm/vnfpkgm/v1/vnf_packages/{}/package_content".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/package_content/upload_from_uri', methods=['POST'])
def post_vnf_package_id_package_content_upload_from_uri(vnf_pkg_id):
    return "POST from /osm/vnfpkgm/v1/vnf_packages/{}/package_content/upload_from_uri".format(vnf_pkg_id)

@vnf_packages.route('/<vnf_pkg_id>/artifacts/<artifact_patch>', methods=['GET'])
def get_vnf_package_id_artifacts(vnf_pkg_id, artifact_patch):
    return "POST from /osm/vnfpkgm/v1/vnf_packages/{}/artifacts/{}".format(vnf_pkg_id, artifact_patch)