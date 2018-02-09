#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cherrypy
import time
import json
import yaml
import html_out as html
import logging
from engine import Engine, EngineException
from dbbase import DbException
from base64 import standard_b64decode
from os import getenv
from http import HTTPStatus
from http.client import responses as http_responses
from codecs import getreader
from os import environ

__author__ = "Alfonso Tierno <alfonso.tiernosepulveda@telefonica.com>"
__version__ = "0.1"
version_date = "Feb 2018"

"""
North Bound Interface  (O: OSM; S: SOL5
URL: /osm                                                       GET     POST    PUT     DELETE  PATCH
        /nsd/v1
            /ns_descriptors                                     O5      O5
                /<nsdInfoId>                                    O5                      O5      5
                    /nsd_content                                O5              O5
            /pnf_descriptors                                    5       5
                /<pnfdInfoId>                                   5                       5       5
                    /pnfd_content                               5               5
            /subcriptions                                       5       5
                /<subcriptionId>                                5                       X

        /vnfpkgm/v1
            /vnf_packages                                       O5      O5
                /<vnfPkgId>                                     O5                      O5      5
                    /vnfd                                       O5      O
                    /package_content                            O5               O5
                        /upload_from_uri                                X
                    /artifacts/<artifactPatch                   X
            /subcriptions                                       X       X
                /<subcriptionId>                                X                       X

        /nslcm/v1
            /ns_instances                                       O5      O5
                /<nsInstanceId>                                 O5                      O5     
                    TO BE COMPLETED                             
            /ns_lcm_op_occs                                     5       5
                /<nsLcmOpOccId>                                 5                       5       5
                    TO BE COMPLETED                             5               5
            /subcriptions                                       5       5
                /<subcriptionId>                                5                       X

query string.
    <attrName>[.<attrName>...]*[.<op>]=<value>[,<value>...]&...
    op: "eq"(or empty to one or the values) | "neq" (to any of the values) | "gt" | "lt" | "gte" | "lte" | "cont" | "ncont"
    all_fields, fields=x,y,.., exclude_default, exclude_fields=x,y,...
        (none)	… same as “exclude_default”
        all_fields	… all attributes.
        fields=<list>	… all attributes except all complex attributes with minimum cardinality of zero that are not conditionally mandatory, and that are not provided in <list>.
        exclude_fields=<list>	… all attributes except those complex attributes with a minimum cardinality of zero that are not conditionally mandatory, and that are provided in <list>.
        exclude_default	… all attributes except those complex attributes with a minimum cardinality of zero that are not conditionally mandatory, and that are part of the "default exclude set" defined in the present specification for the particular resource
        exclude_default and include=<list>	… all attributes except those complex attributes with a minimum cardinality of zero that are not conditionally mandatory and that are part of the "default exclude set" defined in the present specification for the particular resource, but that are not part of <list>
Header field name	Reference	Example	Descriptions
    Accept	IETF RFC 7231 [19]	application/json	Content-Types that are acceptable for the response.
    This header field shall be present if the response is expected to have a non-empty message body.
    Content-Type	IETF RFC 7231 [19]	application/json	The MIME type of the body of the request.
    This header field shall be present if the request has a non-empty message body.
    Authorization	IETF RFC 7235 [22]	Bearer mF_9.B5f-4.1JqM 	The authorization token for the request. Details are specified in clause 4.5.3.
    Range	IETF RFC 7233 [21]	1000-2000	Requested range of bytes from a file
Header field name	Reference	Example	Descriptions
    Content-Type	IETF RFC 7231 [19]	application/json	The MIME type of the body of the response.
    This header field shall be present if the response has a non-empty message body.
    Location	IETF RFC 7231 [19]	http://www.example.com/vnflcm/v1/vnf_instances/123	Used in redirection, or when a new resource has been created.
    This header field shall be present if the response status code is 201 or 3xx.
    In the present document this header field is also used if the response status code is 202 and a new resource was created.
    WWW-Authenticate	IETF RFC 7235 [22]	Bearer realm="example"	Challenge if the corresponding HTTP request has not provided authorization, or error details if the corresponding HTTP request has provided an invalid authorization token.
    Accept-Ranges	IETF RFC 7233 [21]	bytes	Used by the Server to signal whether or not it supports ranges for certain resources.
    Content-Range	IETF RFC 7233 [21]	bytes 21010-47021/ 47022	Signals the byte range that is contained in the response, and the total length of the file.
    Retry-After	IETF RFC 7231 [19]	Fri, 31 Dec 1999 23:59:59 GMT

    or

    120	Used to indicate how long the user agent ought to wait before making a follow-up request.
    It can be used with 503 responses.
    The value of this field can be an HTTP-date or a number of seconds to delay after the response is received.

    #TODO http header for partial uploads: Content-Range: "bytes 0-1199/15000". Id is returned first time and send in following chunks
"""


class NbiException(Exception):

    def __init__(self, message, http_code=HTTPStatus.METHOD_NOT_ALLOWED):
        Exception.__init__(self, message)
        self.http_code = http_code


class Server(object):
    instance = 0
    # to decode bytes to str
    reader = getreader("utf-8")

    def __init__(self):
        self.instance += 1
        self.engine = Engine()

    def _authorization(self):
        token = None
        user_passwd64 = None
        try:
            # 1. Get token Authorization bearer
            auth = cherrypy.request.headers.get("Authorization")
            if auth:
                auth_list = auth.split(" ")
                if auth_list[0].lower() == "bearer":
                    token = auth_list[-1]
                elif auth_list[0].lower() == "basic":
                    user_passwd64 = auth_list[-1]
            if not token:
                if cherrypy.session.get("Authorization"):
                    # 2. Try using session before request a new token. If not, basic authentication will generate
                    token = cherrypy.session.get("Authorization")
                    if token == "logout":
                        token = None   # force Unauthorized response to insert user pasword again
                elif user_passwd64 and cherrypy.request.config.get("auth.allow_basic_authentication"):
                    # 3. Get new token from user password
                    user = None
                    passwd = None
                    try:
                        user_passwd = standard_b64decode(user_passwd64).decode()
                        user, _, passwd = user_passwd.partition(":")
                    except:
                        pass
                    outdata = self.engine.new_token(None, {"username": user, "password": passwd})
                    token = outdata["id"]
                    cherrypy.session['Authorization'] = token
            # 4. Get token from cookie
            # if not token:
            #     auth_cookie = cherrypy.request.cookie.get("Authorization")
            #     if auth_cookie:
            #         token = auth_cookie.value
            return self.engine.authorize(token)
        except EngineException as e:
            if cherrypy.session.get('Authorization'):
                del cherrypy.session['Authorization']
            cherrypy.response.headers["WWW-Authenticate"] = 'Bearer realm="{}"'.format(e)
            raise

    def _format_in(self, kwargs):
        try:
            indata = None
            if cherrypy.request.body.length:
                error_text = "Invalid input format "

                if "Content-Type" in cherrypy.request.headers:
                    if "application/json" in cherrypy.request.headers["Content-Type"]:
                        error_text = "Invalid json format "
                        indata = json.load(self.reader(cherrypy.request.body))
                    elif "application/yaml" in cherrypy.request.headers["Content-Type"]:
                        error_text = "Invalid yaml format "
                        indata = yaml.load(cherrypy.request.body)
                    elif "application/binary" in cherrypy.request.headers["Content-Type"] or \
                         "application/gzip" in cherrypy.request.headers["Content-Type"] or \
                         "application/zip" in cherrypy.request.headers["Content-Type"]:
                        indata = cherrypy.request.body.read()
                    elif "multipart/form-data" in cherrypy.request.headers["Content-Type"]:
                        if "descriptor_file" in kwargs:
                            filecontent = kwargs.pop("descriptor_file")
                            if not filecontent.file:
                                raise NbiException("empty file or content", HTTPStatus.BAD_REQUEST)
                            indata = filecontent.file.read()
                            if filecontent.content_type.value:
                                cherrypy.request.headers["Content-Type"] = filecontent.content_type.value
                    else:
                        # raise cherrypy.HTTPError(HTTPStatus.Not_Acceptable,
                        #                          "Only 'Content-Type' of type 'application/json' or
                        # 'application/yaml' for input format are available")
                        error_text = "Invalid yaml format "
                        indata = yaml.load(cherrypy.request.body)
                else:
                    error_text = "Invalid yaml format "
                    indata = yaml.load(cherrypy.request.body)
            if not indata:
                indata = {}

            if "METHOD" in kwargs:
                method = kwargs.pop("METHOD")
            else:
                method = cherrypy.request.method
            format_yaml = False
            if cherrypy.request.headers.get("Query-String-Format") == "yaml":
                format_yaml = True

            for k, v in kwargs.items():
                if isinstance(v, str):
                    if v == "":
                        kwargs[k] = None
                    elif format_yaml:
                        try:
                            kwargs[k] = yaml.load(v)
                        except:
                            pass
                    elif k.endswith(".gt") or k.endswith(".lt") or k.endswith(".gte") or k.endswith(".lte"):
                        try:
                            kwargs[k] = int(v)
                        except:
                            try:
                                kwargs[k] = float(v)
                            except:
                                pass
                    elif v.find(",") > 0:
                        kwargs[k] = v.split(",")
                elif isinstance(v, (list, tuple)):
                    for index in range(0, len(v)):
                        if v[index] == "":
                            v[index] = None
                        elif format_yaml:
                            try:
                                v[index] = yaml.load(v[index])
                            except:
                                pass

            return indata, method
        except (ValueError, yaml.YAMLError) as exc:
            raise NbiException(error_text + str(exc), HTTPStatus.BAD_REQUEST)
        except KeyError as exc:
            raise NbiException("Query string error: " + str(exc), HTTPStatus.BAD_REQUEST)

    @staticmethod
    def _format_out(data, session=None):
        """
        return string of dictionary data according to requested json, yaml, xml. By default json
        :param data: response to be sent. Can be a dict or text
        :param session:
        :return: None
        """
        if "Accept" in cherrypy.request.headers:
            accept = cherrypy.request.headers["Accept"]
            if "application/json" in accept:
                cherrypy.response.headers["Content-Type"] = 'application/json; charset=utf-8'
                a = json.dumps(data, indent=4) + "\n"
                return a.encode("utf8")
            elif "text/html" in accept:
                return html.format(data, cherrypy.request, cherrypy.response, session)

            elif "application/yaml" in accept or "*/*" in accept:
                pass
            else:
                raise cherrypy.HTTPError(HTTPStatus.NOT_ACCEPTABLE.value,
                                         "Only 'Accept' of type 'application/json' or 'application/yaml' "
                                         "for output format are available")
        cherrypy.response.headers["Content-Type"] = 'application/yaml'
        return yaml.safe_dump(data, explicit_start=True, indent=4, default_flow_style=False, tags=False,
                              encoding='utf-8', allow_unicode=True)  # , canonical=True, default_style='"'

    @cherrypy.expose
    def index(self, *args, **kwargs):
        session = None
        try:
            if cherrypy.request.method == "GET":
                session = self._authorization()
                outdata = "Index page"
            else:
                raise cherrypy.HTTPError(HTTPStatus.METHOD_NOT_ALLOWED.value,
                                 "Method {} not allowed for tokens".format(cherrypy.request.method))

            return self._format_out(outdata, session)

        except EngineException as e:
            cherrypy.log("index Exception {}".format(e))
            cherrypy.response.status = e.http_code.value
            return self._format_out("Welcome to OSM!", session)

    @cherrypy.expose
    def token(self, *args, **kwargs):
        if not args:
            raise NbiException("URL must contain at least 'item/version'", HTTPStatus.METHOD_NOT_ALLOWED)
        version = args[0]
        if version != 'v1':
            raise NbiException("URL version '{}' not supported".format(version), HTTPStatus.METHOD_NOT_ALLOWED)
        session = None
        # self.engine.load_dbase(cherrypy.request.app.config)
        try:
            indata, method = self._format_in(kwargs)
            if method == "GET":
                session = self._authorization()
                if len(args) >= 2:
                    outdata = self.engine.get_token(session, args[1])
                else:
                    outdata = self.engine.get_token_list(session)
            elif method == "POST":
                try:
                    session = self._authorization()
                except:
                    session = None
                if kwargs:
                    indata.update(kwargs)
                outdata = self.engine.new_token(session, indata, cherrypy.request.remote)
                session = outdata
                cherrypy.session['Authorization'] = outdata["_id"]
                # cherrypy.response.cookie["Authorization"] = outdata["id"]
                # cherrypy.response.cookie["Authorization"]['expires'] = 3600
            elif method == "DELETE":
                if len(args) >= 2 and "logout" not in args:
                    token_id = args[1]
                elif "id" in kwargs:
                    token_id = kwargs["id"]
                else:
                    session = self._authorization()
                    token_id = session["_id"]
                outdata = self.engine.del_token(token_id)
                session = None
                cherrypy.session['Authorization'] = "logout"
                # cherrypy.response.cookie["Authorization"] = token_id
                # cherrypy.response.cookie["Authorization"]['expires'] = 0
            else:
                raise NbiException("Method {} not allowed for token".format(method), HTTPStatus.METHOD_NOT_ALLOWED)
            return self._format_out(outdata, session)
        except (NbiException, EngineException, DbException) as e:
            cherrypy.log("tokens Exception {}".format(e))
            cherrypy.response.status = e.http_code.value
            problem_details = {
                "code": e.http_code.name,
                "status": e.http_code.value,
                "detail": str(e),
            }
            return self._format_out(problem_details, session)

    @cherrypy.expose
    def test(self, *args, **kwargs):
        thread_info = None
        if args and args[0] == "init":
            try:
                # self.engine.load_dbase(cherrypy.request.app.config)
                self.engine.create_admin()
                return "Done. User 'admin', password 'admin' created"
            except Exception:
                cherrypy.response.status = HTTPStatus.FORBIDDEN.value
                return self._format_out("Database already initialized")
        elif args and args[0] == "prune":
            return self.engine.prune()
        elif args and args[0] == "login":
            if not cherrypy.request.headers.get("Authorization"):
                cherrypy.response.headers["WWW-Authenticate"] = 'Basic realm="Access to OSM site", charset="UTF-8"'
                cherrypy.response.status = HTTPStatus.UNAUTHORIZED.value
        elif args and args[0] == "login2":
            if not cherrypy.request.headers.get("Authorization"):
                cherrypy.response.headers["WWW-Authenticate"] = 'Bearer realm="Access to OSM site"'
                cherrypy.response.status = HTTPStatus.UNAUTHORIZED.value
        elif args and args[0] == "sleep":
            sleep_time = 5
            try:
                sleep_time = int(args[1])
            except Exception:
                cherrypy.response.status = HTTPStatus.FORBIDDEN.value
                return self._format_out("Database already initialized")
            thread_info = cherrypy.thread_data
            print(thread_info)
            time.sleep(sleep_time)
            # thread_info
        elif len(args) >= 2 and args[0] == "message":
            topic = args[1]
            try:
                for k, v in kwargs.items():
                    self.engine.msg.write(topic, k, yaml.load(v))
                return "ok"
            except Exception as e:
                return "Error: " + format(e)

        return_text = (
            "<html><pre>\nheaders:\n  args: {}\n".format(args) +
            "  kwargs: {}\n".format(kwargs) +
            "  headers: {}\n".format(cherrypy.request.headers) +
            "  path_info: {}\n".format(cherrypy.request.path_info) +
            "  query_string: {}\n".format(cherrypy.request.query_string) +
            "  session: {}\n".format(cherrypy.session) +
            "  cookie: {}\n".format(cherrypy.request.cookie) +
            "  method: {}\n".format(cherrypy.request.method) +
            " session: {}\n".format(cherrypy.session.get('fieldname')) +
            "  body:\n")
        return_text += "    length: {}\n".format(cherrypy.request.body.length)
        if cherrypy.request.body.length:
            return_text += "    content: {}\n".format(
                str(cherrypy.request.body.read(int(cherrypy.request.headers.get('Content-Length', 0)))))
        if thread_info:
            return_text += "thread: {}\n".format(thread_info)
        return_text += "</pre></html>"
        return return_text

    @cherrypy.expose
    def default(self, *args, **kwargs):
        session = None
        try:
            if not args or len(args) < 2:
                raise NbiException("URL must contain at least 'item/version'", HTTPStatus.METHOD_NOT_ALLOWED)
            item = args[0]
            version = args[1]
            if item not in ("token", "user", "project", "vnfpkgm", "nsd", "nslcm"):
                raise NbiException("URL item '{}' not supported".format(item), HTTPStatus.METHOD_NOT_ALLOWED)
            if version != 'v1':
                raise NbiException("URL version '{}' not supported".format(version), HTTPStatus.METHOD_NOT_ALLOWED)

            # self.engine.load_dbase(cherrypy.request.app.config)
            session = self._authorization()
            indata, method = self._format_in(kwargs)
            _id = None

            if item == "nsd":
                item = "nsds"
                if len(args) < 3 or args[2] != "ns_descriptors":
                    raise NbiException("only ns_descriptors is allowed", HTTPStatus.METHOD_NOT_ALLOWED)
                if len(args) > 3:
                    _id = args[3]
                if len(args) > 4 and args[4] != "nsd_content":
                    raise NbiException("only nsd_content is allowed", HTTPStatus.METHOD_NOT_ALLOWED)
            elif item == "vnfpkgm":
                item = "vnfds"
                if len(args) < 3 or args[2] != "vnf_packages":
                    raise NbiException("only vnf_packages is allowed", HTTPStatus.METHOD_NOT_ALLOWED)
                if len(args) > 3:
                    _id = args[3]
                if len(args) > 4 and args[4] not in ("vnfd", "package_content"):
                    raise NbiException("only vnfd or package_content are allowed", HTTPStatus.METHOD_NOT_ALLOWED)
            elif item == "nslcm":
                item = "nsrs"
                if len(args) < 3 or args[2] != "ns_instances":
                    raise NbiException("only ns_instances is allowed", HTTPStatus.METHOD_NOT_ALLOWED)
                if len(args) > 3:
                    _id = args[3]
                if len(args) > 4:
                    raise NbiException("This feature is not implemented", HTTPStatus.METHOD_NOT_ALLOWED)
            else:
                if len(args) >= 3:
                    _id = args[2]
                item += "s"

            if method == "GET":
                if not _id:
                    outdata = self.engine.get_item_list(session, item, kwargs)
                else:  # len(args) > 1
                    outdata = self.engine.get_item(session, item, _id)
            elif method == "POST":
                id, completed = self.engine.new_item(session, item, indata, kwargs, cherrypy.request.headers)
                if not completed:
                    cherrypy.response.headers["Transaction-Id"] = id
                    cherrypy.response.status = HTTPStatus.CREATED.value
                else:
                    cherrypy.response.headers["Location"] = cherrypy.request.base + "/osm/" + "/".join(args[0:3]) + "/" + id
                outdata = {"id": id}
            elif method == "DELETE":
                if not _id:
                    outdata = self.engine.del_item_list(session, item, kwargs)
                else:  # len(args) > 1
                    outdata = self.engine.del_item(session, item, _id)
            elif method == "PUT":
                if not _id:
                    raise NbiException("Missing '/<id>' at the URL to identify item to be updated",
                                       HTTPStatus.METHOD_NOT_ALLOWED)
                elif not indata and not kwargs:
                    raise NbiException("Nothing to update. Provide payload and/or query string",
                                       HTTPStatus.BAD_REQUEST)
                outdata = {"id": self.engine.edit_item(session, item, args[1], indata, kwargs)}
            else:
                raise NbiException("Method {} not allowed".format(method), HTTPStatus.METHOD_NOT_ALLOWED)
            return self._format_out(outdata, session)
        except (NbiException, EngineException, DbException) as e:
            cherrypy.log("Exception {}".format(e))
            cherrypy.response.status = e.http_code.value
            problem_details = {
                "code": e.http_code.name,
                "status": e.http_code.value,
                "detail": str(e),
            }
            return self._format_out(problem_details, session)
            # raise cherrypy.HTTPError(e.http_code.value, str(e))


# def validate_password(realm, username, password):
#     cherrypy.log("realm "+ str(realm))
#     if username == "admin" and password == "admin":
#         return True
#     return False


def _start_service():
    """
    Callback function called when cherrypy.engine starts
    Override configuration with env variables
    Set database, storage, message configuration
    Init database with admin/admin user password
    """
    cherrypy.log.error("Starting osm_nbi")
    # update general cherrypy configuration
    update_dict = {}

    engine_config = cherrypy.tree.apps['/osm'].config
    for k, v in environ.items():
        if not k.startswith("OSMNBI_"):
            continue
        k1, _,  k2 = k[7:].lower().partition("_")
        if not k2:
            continue
        try:
            # update static configuration
            if k == 'OSMNBI_STATIC_DIR':
                engine_config["/static"]['tools.staticdir.dir'] = v
                engine_config["/static"]['tools.staticdir.on'] = True
            elif k == 'OSMNBI_SOCKET_PORT' or k == 'OSMNBI_SERVER_PORT':
                update_dict['server.socket_port'] = int(v)
            elif k == 'OSMNBI_SOCKET_HOST' or k == 'OSMNBI_SERVER_HOST':
                update_dict['server.socket_host'] = v
            elif k1 == "server":
                update_dict['server' + k2] = v
                # TODO add more entries
            elif k1 in ("message", "database", "storage"):
                if k2 == "port":
                    engine_config[k1][k2] = int(v)
                else:
                    engine_config[k1][k2] = v
        except ValueError as e:
            cherrypy.log.error("Ignoring environ '{}': " + str(e))
        except Exception as e:
            cherrypy.log.warn("skipping environ '{}' on exception '{}'".format(k, e))

    if update_dict:
        cherrypy.config.update(update_dict)

    # logging cherrypy
    log_format_simple = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(message)s"
    log_formatter_simple = logging.Formatter(log_format_simple, datefmt='%Y-%m-%dT%H:%M:%S')
    logger_server = logging.getLogger("cherrypy.error")
    logger_access = logging.getLogger("cherrypy.access")
    logger_cherry = logging.getLogger("cherrypy")
    logger_nbi = logging.getLogger("nbi")

    if "logfile" in engine_config["global"]:
        file_handler = logging.handlers.RotatingFileHandler(engine_config["global"]["logfile"],
                                                            maxBytes=100e6, backupCount=9, delay=0)
        file_handler.setFormatter(log_formatter_simple)
        logger_cherry.addHandler(file_handler)
        logger_nbi.addHandler(file_handler)
    else:
        for format_, logger in {"nbi.server": logger_server,
                                "nbi.access": logger_access,
                                "%(name)s %(filename)s:%(lineno)s": logger_nbi
                                }.items():
            log_format_cherry = "%(asctime)s %(levelname)s {} %(message)s".format(format_)
            log_formatter_cherry = logging.Formatter(log_format_cherry, datefmt='%Y-%m-%dT%H:%M:%S')
            str_handler = logging.StreamHandler()
            str_handler.setFormatter(log_formatter_cherry)
            logger.addHandler(str_handler)

    if engine_config["global"].get("loglevel"):
        logger_cherry.setLevel(engine_config["global"]["loglevel"])
        logger_nbi.setLevel(engine_config["global"]["loglevel"])

    # logging other modules
    for k1, logname in {"message": "nbi.msg", "database": "nbi.db", "storage": "nbi.fs"}.items():
        engine_config[k1]["logger_name"] = logname
        logger_module = logging.getLogger(logname)
        if "logfile" in engine_config[k1]:
            file_handler = logging.handlers.RotatingFileHandler(engine_config[k1]["logfile"],
                                                             maxBytes=100e6, backupCount=9, delay=0)
            file_handler.setFormatter(log_formatter_simple)
            logger_module.addHandler(file_handler)
        if "loglevel" in engine_config[k1]:
            logger_module.setLevel(engine_config[k1]["loglevel"])
    # TODO add more entries, e.g.: storage
    cherrypy.tree.apps['/osm'].root.engine.start(engine_config)
    try:
        cherrypy.tree.apps['/osm'].root.engine.create_admin()
    except EngineException:
        pass
    # getenv('OSMOPENMANO_TENANT', None)


def _stop_service():
    """
    Callback function called when cherrypy.engine stops
    TODO: Ending database connections.
    """
    cherrypy.tree.apps['/osm'].root.engine.stop()
    cherrypy.log.error("Stopping osm_nbi")

def nbi():
    # conf = {
    #     '/': {
    #         #'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    #         'tools.sessions.on': True,
    #         'tools.response_headers.on': True,
    #         # 'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    #     }
    # }
    # cherrypy.Server.ssl_module = 'builtin'
    # cherrypy.Server.ssl_certificate = "http/cert.pem"
    # cherrypy.Server.ssl_private_key = "http/privkey.pem"
    # cherrypy.Server.thread_pool = 10
    # cherrypy.config.update({'Server.socket_port': config["port"], 'Server.socket_host': config["host"]})

    # cherrypy.config.update({'tools.auth_basic.on': True,
    #    'tools.auth_basic.realm': 'localhost',
    #    'tools.auth_basic.checkpassword': validate_password})
    cherrypy.engine.subscribe('start', _start_service)
    cherrypy.engine.subscribe('stop', _stop_service)
    cherrypy.quickstart(Server(), '/osm', "nbi.cfg")


if __name__ == '__main__':
    nbi()