from flask import Blueprint

subscriptions = Blueprint('vnfpkgm_v1_subscriptions', __name__)

@subscriptions.route('/', methods=['GET'])
def get_subscriptions():
    return "GET from /osm/vnfpkgm/v1/subscriptions"

@subscriptions.route('/', methods=['POST'])
def post_subscriptions():
    return "POST from /osm/vnfpkgm/v1/subscriptions"

@subscriptions.route('/<subscription_id>', methods=['GET'])
def get_subscription_id(subscription_id):
    return "GET from /osm/vnfpkgm/v1/subscriptions/{}".format(subscription_id)

@subscriptions.route('/<subscription_id>', methods=['DELETE'])
def delete_subscription_id(subscription_id):
    return "DELETE from /osm/vnfpkgm/v1/subscriptions/{}".format(subscription_id)