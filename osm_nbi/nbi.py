import flask
from base64 import standard_b64decode

from engine import Engine, EngineException

from nsd_v1.ns_descriptors import ns_descriptors as nsd_v1_ns_descriptors
from nsd_v1.pnf_descriptors import pnf_descriptors as nsd_v1_pnf_descriptors
from nsd_v1.subscriptions import subscriptions as nsd_v1_subscriptions

from vnfpkgm_v1.vnf_packages import vnf_packages as vnfpkgm_v1_vnf_packages
from vnfpkgm_v1.subscriptions import subscriptions as vnfpkgm_v1_subscriptions

from nslcm_v1.ns_instances import ns_instances as nslcm_v1_ns_instances
from nslcm_v1.ns_lcm_op_occs import ns_lcm_op_occs as nslcm_v1_ns_lcm_op_occs
from nslcm_v1.subscriptions import subscriptions as nslcm_v1_subscriptions

app = flask.Flask(__name__)
app.url_map.strict_slashes = False
    

@app.before_request
def before_request():
    engine = Engine()
    flask.g['engine'] = engine
    
    token = None
    user_passwd64 = None
    try:
        # 1. Get token Authorization bearer
        auth = flask.request.headers.get("Authorization")
        if auth:
            auth_list = auth.split(" ")
            if auth_list[0].lower() == "bearer":
                token = auth_list[-1]
            elif auth_list[0].lower() == "basic":
                user_passwd64 = auth_list[-1]
        if not token:
            if flask.session.get("Authorization"):
                # 2. Try using session before request a new token. If not, basic authentication will generate
                token = flask.session.get("Authorization")
                if token == "logout":
                    token = None   # force Unauthorized response to insert user pasword again
            elif user_passwd64 and flask.request.config.get("auth.allow_basic_authentication"):
                # 3. Get new token from user password
                user = None
                passwd = None
                try:
                    user_passwd = standard_b64decode(user_passwd64).decode()
                    user, _, passwd = user_passwd.partition(":")
                except:
                    pass
                outdata = engine.new_token(None, {"username": user, "password": passwd}, flask.request.remote_addr)
                token = outdata["id"]
                flask.session['Authorization'] = token
        # 4. Get token from cookie
        # if not token:
        #     auth_cookie = cherrypy.request.cookie.get("Authorization")
        #     if auth_cookie:
        #         token = auth_cookie.value
        flask.g['session'] = engine.authorize(token)
    except EngineException as e:
        if flask.session.get('Authorization'):
            del flask.session['Authorization']
        # flask.response.headers["WWW-Authenticate"] = 'Bearer realm="{}"'.format(e)
        flask.abort(401)

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