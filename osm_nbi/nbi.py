from flask import Flask

from nsd_v1.ns_descriptors import ns_descriptors as nsd_v1_ns_descriptors
from nsd_v1.pnf_descriptors import pnf_descriptors as nsd_v1_pnf_descriptors
from nsd_v1.subscriptions import subscriptions as nsd_v1_subscriptions

from vnfpkgm_v1.vnf_packages import vnf_packages as vnfpkgm_v1_vnf_packages
from vnfpkgm_v1.subscriptions import subscriptions as vnfpkgm_v1_subscriptions

from nslcm_v1.ns_instances import ns_instances as nslcm_v1_ns_instances
from nslcm_v1.ns_lcm_op_occs import ns_lcm_op_occs as nslcm_v1_ns_lcm_op_occs
from nslcm_v1.subscriptions import subscriptions as nslcm_v1_subscriptions

app = Flask(__name__)
app.url_map.strict_slashes = False

# NSD Routes
app.register_blueprint(nsd_v1_ns_descriptors, url_prefix='/osm/nsd/v1/ns_descriptors')
app.register_blueprint(nsd_v1_pnf_descriptors, url_prefix='/osm/nsd/v1/pnf_descriptors')
app.register_blueprint(nsd_v1_subscriptions, url_prefix='/osm/nsd/v1/subscriptions')

# VNF Package Routes
app.register_blueprint(vnfpkgm_v1_vnf_packages, url_prefix='/osm/vnfpkgm/v1/vnf_packages')
app.register_blueprint(vnfpkgm_v1_subscriptions, url_prefix='/osm/vnfpkgm/v1/subcriptions')

# NS LCM Routes
app.register_blueprint(nslcm_v1_ns_instances, url_prefix='/osm/nslcm/v1/ns_instances')
app.register_blueprint(nslcm_v1_ns_lcm_op_occs, url_prefix='/osm/nslcm/v1/ns_lcm_op_occs')
app.register_blueprint(nslcm_v1_subscriptions, url_prefix='/osm/nslcm/v1/subcriptions')